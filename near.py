import math, csv, sys, os, re
from collections import defaultdict
from datetime import date, timedelta
from urllib import urlopen
from pprint import pprint
from waitrose import get_waitrose
from read_infobox import get_stations
from lxml.html import parse, tostring, fromstring

def next_monday():
    return date.today() + timedelta(7 - date.today().weekday())

url = 'http://ojp.nationalrail.co.uk/service/timesandfares/%s/%s/' \
        + next_monday().strftime('%d%m%y') + '/1000/dep'

destinations = ('London', 'WEY', 'BRI', 'NLS')

re_duration = re.compile('(?:(\d+)h\r\n\t\t)?(\d+)m')
def read_times(page):
    doc = fromstring(page)

    skip = set('\t\n')
    def strip_whitespace(s):
        return s.strip()

    tbody = doc.get_element_by_id('outboundFaresTable')[1]
    times = []
    for tr in tbody:
        if len(tr) < 4:
            continue
        m = re_duration.match(tr[4].text_content().strip())
        changes = int(tr[5].text_content().strip())
        times.append((int(m.group(1) or 0) * 60 + int(m.group(2)), changes))
    return min(times)

miles = 3960
def distance(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi / 180.0
        
    phi1, phi2 = (90 - lat1)*degrees_to_radians, (90 - lat2)*degrees_to_radians
    theta1, theta2 = long1*degrees_to_radians, long2*degrees_to_radians
        
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    return arc * miles # http://www.johndcook.com/python_longitude_latitude.html

def waitrose_and_stations():
    skip = set(['HXX', 'RDS', 'BBS', 'HWV', 'MUF'])
    #must_have = set(['Fish', 'Delicatessen', 'Meat', 'Bakery'])
    must_have = set(['Delicatessen'])
    stations = [i for i in get_stations() if i['code'] not in skip]

    if not os.path.exists('nationalrail'):
        os.mkdir('nationalrail')
    for w in get_waitrose():
        if not set(w['counters']) >= must_have:
            continue
        for s in stations:
            s['dist'] = distance(w['latitude'], w['longitude'], s['latitude'], s['longitude'])
            if s['dist'] > 4:
                continue
            for dest in destinations:
                if dest == s['code']:
                    s[dest + '_mins'] = 0
                    s[dest + '_changes'] = 0
                    continue
                if not os.path.exists('nationalrail/' + dest):
                    os.mkdir('nationalrail/' + dest)
                f = 'nationalrail/%s/%s.html' % (dest, s['code'])
                if os.path.exists(f):
                    page = open(f).read()
                else:
                    print s['code'], '%25s' % s['name'], url % (s['code'], dest)
                    page = urlopen(url % (s['code'], dest)).read()
                    open(f, 'w').write(page)
                s[dest + '_mins'], s[dest + '_changes'] = read_times(page)
                if dest == 'London' and s[dest + '_mins'] > 150:
                    break
            w.setdefault('stations', []).append(s)
        yield w
