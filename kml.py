from near import waitrose_and_stations
from pprint import pprint

out = open('ws.kml', 'w')
print >> out, '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document><name>Waitrose</name>'''

def hm(m):
    return '%dh%d' % (m / 60, m % 60)

for w in waitrose_and_stations():
    if 'stations' not in w:
        continue
    fast = {}

    for dest in ('London', 'WEY', 'NLS', 'BRI'):
        if any(dest + '_mins' not in s for s in w['stations']):
            break
        fast[dest] = min((s for s in w['stations']), key=lambda s:s.get(dest + '_mins', 0))
        print fast[dest].get(dest + '_mins', 0), dest
        for s in w['stations']:
            if dest + '_mins' in s:
                print '   ', s['code'], s[dest + '_mins'], s[dest + '_changes'], s['name']
    print
    if fast['London']['London_mins'] > 150:
        continue
    if 'WEY' not in fast or 'BRI' not in fast:
        continue
    if any((fast[dest].get(dest + '_mins', 0) > 60 * 3.5 for dest in ('WEY', 'BRI'))):
        continue

    print >> out, '''  <Placemark>
    <name>%s (%s)</name>
    <description><![CDATA[
    
    <a href="http://www.rightmove.co.uk/property-for-sale/search.html?searchType=SALE&previousSearchLocation=&searchLocation=%s&radius=1.0&displayPropertyType=houses&minBedrooms=2&maxPrice=250000&_includeSSTC=on&auction=false">for sale</a>
    <a href="http://www.rightmove.co.uk/property-to-rent/search.html?searchType=RENT&previousSearchLocation=&searchLocation=%s&radius=1.0&displayPropertyType=houses&minBedrooms=2&sortByPriceDescending=false">for rent</a>
    <br>''' % (w['name'], w['postcode'], w['postcode'], w['postcode'])

    for s in sorted(w['stations'], key=lambda s:s['dist']):
        print >> out, '''<a href="http://en.wikipedia.org/wiki/%s">%s</a> (%.1f miles)<br>''' % (s['wikipedia'].replace(' ', '_'), s['name'], s['dist'])

    for dest in ('London', 'WEY', 'NLS', 'BRI'):
        s = fast[dest]
        print >> out, '%s -> %s: %s, %s changes<br>' % (s['code'], dest, hm(s.get(dest + '_mins', 0)), s.get(dest + '_changes', 0))

    print >> out, '''
    Counters: %s ]]>
    </description>
    <Point>
      <coordinates>%s,%s</coordinates>
    </Point>
  </Placemark>''' % ('; '.join(w['counters']), w['longitude'], w['latitude'])

print >> out, '</Document></kml>'
