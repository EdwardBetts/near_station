from lxml import html
import csv, re, os, json
from urllib import urlopen

def find_counters(page):
    state = 'start'
    for line in page.splitlines():
        if state == 'start' and '<h2>Food Counters & Ranges</h2>' in line:
            state = '/ul'
            continue
        if state == '/a':
            if '</a>' in line:
                state = '/ul'
                continue
            if line.strip():
                yield line.strip()
        if state == '/ul':
            if '<a href="#" class="infoPopup" id="' in line:
                state = '/a'
                continue

            if '</ul>' in line:
                return

def get_waitrose():
    if not os.exists.path('cache'):
        os.mkdir('cache')
    f = 'cache/waitrose'
    if os.path.exists(f):
        return json.load(open(f))

    url = 'http://www.waitrose.com/content/waitrose/en/bf_home/bf.html'
    re_hidden = re.compile('<input type="hidden" id="([^_]+)_1" value="(.*?)" />')

    doc = html.parse(url).getroot()

    stores = []
    url = 'http://www.waitrose.com/branches/branchdetails.aspx?uid='
    for option in doc.get_element_by_id('_branchDropdown'):
        uid = option.get("value")
        page = urlopen(url + uid).read()
        data = dict(m.groups() for m in re_hidden.finditer(page))
        if not data.get('latitude'):
            continue
        print uid, option.text.strip()
        stores.append({
            'uid': uid,
            'name': option.text.strip(),
            'postcode': data.get('postCode'),
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'counters': list(find_counters(page)),
        })

    json.dump(stores, open(f, 'w'), indent=2)
    return stores
