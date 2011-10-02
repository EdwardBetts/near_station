import os, codecs, re, json
from parse_infobox import find_templates, parse_template
from pprint import pprint

re_dec = re.compile('^-?\d+\.\d+$')
re_coord_dec1 = re.compile('^\{\{coord\s*\|(\d+\.\d+)\|(-?\d+\.\d+)', re.I)
re_coord_dec2 = re.compile('^\{\{coord\s*\|(\d+\.\d+)\|N\|\s*(\d+\.\d+)\|([EW])', re.I)
re_coord_dms = re.compile('^\{\{coord\s*\|(\d+)\|(\d+)\|(\d+(?:\.\d+)?)\|N\|\s*(\d+)\|(\d+)\|(\d+(?:\.\d+)?)\|([EW])', re.I)
re_coord_dm = re.compile('^\{\{coord\s*\|(\d+)\|(\d+(?:\.\d+)?)\|N\|\s*(\d+)\|(\d+(?:\.\d+)?)\|([EW])', re.I)
re_decdeg = re.compile('^\{\{decdeg\|(\d+)\|(\d+(?:\.\d+)?)\|(\d*(?:\.\d+)?)\|([NSEW])')

re_nowrap = re.compile(r'^\{\{nowrap\|([^}]+)\}\}$')
re_rail_symbol = re.compile('^([^{]+) (?:<big>)?\{\{[Rr][^}]+\}\}(?:</big>)?')
re_name_br = re.compile('^([^<]+)<br>')

def find_infobox_and_coord(page):
    reply = {}
    for name, t in find_templates(page):
        if 'infobox' not in reply and ('infobox' in name.lower() or 'uk stations' in name.lower()):
            reply['name'], reply['infobox'] = name, parse_template(t)
        if 'coord' not in reply and name.lower().startswith('coord'):
            reply['coord'] = t
    return reply

def dms_to_dec(d, m, s):
    return d + m / 60 + s / 3600

def parse_coord(coord):
    m = re_coord_dec1.match(coord)
    if m:
        return map(float, m.groups())
    m = re_coord_dec2.match(coord)
    if m:
        lat = float(m.group(1))
        lon = float(m.group(2)) * ew[m.group(3)]
        return (lat, lon)
    m = re_coord_dm.match(coord)
    if m:
        lat = float(m.group(1)) + float(m.group(2)) / 60
        lon = (float(m.group(3)) + float(m.group(4)) / 60) * ew[m.group(5)]
        return (lat, lon)
    m = re_coord_dms.match(coord)
    lat = apply(dms_to_dec, map(float, m.group(1,2,3)))
    lon = apply(dms_to_dec, map(float, m.group(4,5,6))) * ew[m.group(7)]
    return (lat, lon)

ew = {'E': 1, 'W': -1, 'N': 1, 'S': -1 }

def get_stations():
    if not os.path.exists('cache'):
        os.mkdir('cache')
    cache = 'cache/stations'
    if os.path.exists(cache):
        return json.load(open(cache))

    to_skip = ['Bermuda railway station', 'tube station', 'DLR station']
    d = 'wiki_stations'
    stations = []
    for f in os.listdir(d):
        if any(i in f for i in to_skip):
            continue
        content = codecs.open(d + '/' + f, 'r', 'utf-8').read()
        found = find_infobox_and_coord(content)
        if 'london' in found['name'].lower():
            continue
        infobox = dict(found['infobox'])

        code = infobox.get('code') or infobox.get('railcode')
        if not code:
            continue

        name = infobox['name'].replace(' {{Access icon}}', '')
        for pat in re_nowrap, re_rail_symbol, re_name_br:
            m = pat.match(name)
            if m:
                name = m.group(1)
        station = { 'name': name, 'code': code, 'wikipedia': f[:-5]}

        assert '{' not in name and '|' not in name and '<' not in name

        assert found.get('coord') or ('latitude' in infobox and 'longitude' in infobox)

        if 'Category:Railway termini in London' in content:
            continue
        if found.get('coord'):
            if found['coord'].startswith('{{coord missing') and 'Category:Proposed railway station' in content:
                continue
            station['latitude'], station['longitude'] = parse_coord(found['coord'])
        if not station.get('latitude'):
            for k, v in found['infobox']:
                if v and k in ['latitude', 'longitude']:
                    if re_dec.match(v):
                        station[str(k)] = float(v)
                        continue
                    m = re_decdeg.match(v)
                    assert m
                    station[str(k)] = apply(dms_to_dec, map(lambda i: float(i) if i else 0, m.group(1,2,3))) * ew[m.group(4)]

        stations.append(station)
    json.dump(stations, open(cache, 'w'), indent=2)
    return stations

get_stations()
