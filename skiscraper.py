"""
Sækir opnunartíma í Bláfjöllum og Skálafelli á skidasvaedi.is
"""

import re
from datetime import datetime

import bs4
import requests
from tabulate import tabulate


def parse_lift_opening_dl(dl):
    for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
        name = dt.text.strip()
        is_open = 'open' in dd.attrs.get('class', [])
        yield name, is_open


def parse_opening_info_div(div):
    area_name_h2s = div.find_all('h2')
    lift_opening_dls = div.find_all('dl')
    for h2, dl in zip(area_name_h2s, lift_opening_dls):
        area_name = h2.text.strip()
        for lift_name, is_open in parse_lift_opening_dl(dl):
            yield area_name, lift_name, is_open


def parse_last_change_span(span):
    pattern = r'\w+\s+\w+:\s+(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2})'
    datestr = re.match(pattern, span.text).group(1)
    last_changed_at = datetime.strptime(datestr, '%d.%m.%Y %H:%M')
    return last_changed_at


def parse_mountain_div(div):
    last_change_span, = div.select('.lastchange span')
    last_changed_at = parse_last_change_span(last_change_span)
    opening_info_divs = div.select('.opening-info')
    for opening_info_div in opening_info_divs:
        for area_name, lift_name, is_open in parse_opening_info_div(opening_info_div):
            yield area_name, lift_name, is_open, last_changed_at


def main():
    response = requests.get('http://www.skidasvaedi.is/desktopdefault.aspx')
    html = response.text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    tabs = (
        ('Bláfjöll', '#tab-1'),
        ('Skálafell', '#tab-2')
    )
    table = [['Fjall', 'Svæði', 'Lyfta', 'Er opin', 'Síðast uppfært']]
    for mountain_name, selector in tabs:
        main_div, = soup.select(selector)
        for area_name, lift_name, is_open, last_changed_at in parse_mountain_div(main_div):
            lift_name = lift_name if len(lift_name) < 50 else lift_name[:47] + '...'
            table.append([mountain_name, area_name, lift_name, is_open, last_changed_at])
    print(tabulate(table, headers="firstrow"))


if __name__ == "__main__":
    main()
