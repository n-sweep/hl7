#!/usr/bin/env python3
# Webscraping HL7 data file standards

import os
import re
import json
import requests
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString

base_url = 'http://www.hl7.eu/HL7v2x/v28/std28'
contents = 'hl7.html'


def request(endpoint):
    return requests.get(os.path.join(base_url, endpoint))


def hot_soup(endpoint):
    r = request(endpoint)
    return bs(r.content, 'html.parser')


def get_all_segments(soup):
    seg_rx = r'(.*?)\s+([A-Z\d]{3}) - (.*?) Segment'
    field_rx = r'-(\d+)\s+(.*)$'

    segments = {}
    for a in soup.find_all('a', text=re.compile(seg_rx)):
        fields = (
            a.parent.next_sibling.next_sibling
            .find_all('a', text=re.compile(field_rx))
        )
        ch, seg, title = re.search(seg_rx, a.text).groups()
        segments[seg] = {'title': title, 'fields': {}}

        for f in fields:
            i, text = re.search(field_rx, f.text).groups()
            segments[seg]['fields'][i] = {'text': text, 'href': f['href']}

    return segments


def find_field_children(soup, field):
    endpoint, hid = field['href'].split('#')

    r = soup.find('a', id=hid)
    if not r:
        soup = hot_soup(endpoint)
        r = soup.find('a', id=hid)

    output = []
    for child in list(r.children)[:-1]:
        if isinstance(child, NavigableString):
            continue

        p = child.findChildren('p', recursive=True)
        if p and not isinstance(p, int):
            output.append(p)

    return soup, output


def main():
    soup = hot_soup(contents)
    segments = get_all_segments(soup)

    for seg, vals in segments.items():
        for i, field in vals['fields'].items():
            soup, children = find_field_children(soup, field)
            for child in children:
                print(child)
                print('')
            # for child in children:
                # txt = child.text.strip()
                # desc_rx = r'(Definition|Components|Subcomponents for .*? \(\w*\)): (.*)$'
                # g = re.search(desc_rx, txt)
        break


# def main():
    # soup = hot_soup(contents)
    # soup = hot_soup('ch02.html')
    # r = soup.find(id='Heading239')
    # children = list(r.children)[:-1]
    # for child in children:
        # print(child)


if __name__ == '__main__':
    main()
