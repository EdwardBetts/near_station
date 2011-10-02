#!/usr/bin/python
import urllib, json, os, codecs

def quote(s):
    return urllib.quote_plus(s.encode('utf-8'))

query_url = 'http://en.wikipedia.org/w/api.php?format=json&action=query&'
def get(params):
    return json.load(urllib.urlopen(query_url + params))

content_params = 'prop=revisions&rvprop=content|timestamp&titles='
def get_content(title):
    ret = get(content_params + quote(title))
    rev = ret['query']['pages'].values()[0]['revisions'][0]
    return rev['*']

embeddedin_params = 'list=embeddedin&eilimit=500&einamespace=0&eifilterredir=nonredirects&eititle=Template:'
def wiki_embeddedin(q):
    ret = get(embeddedin_params + quote(q))
    docs = ret['query']['embeddedin']
    for doc in docs:
        yield doc
    while 'query-continue' in ret:
        eicontinue = ret['query-continue']['embeddedin']['eicontinue']
        ret = get(embeddedin_params + quote(q) + '&eicontinue=' + quote(eicontinue))
        for doc in ret['query']['embeddedin']:
            yield doc

#for t in 'Infobox GB station', 'Infobox London station':
t = 'Infobox GB station'
if not os.path.exists('wikipedia'):
    os.mkdir('wikipedia')
for doc in wiki_embeddedin(t):
    filename = 'wikipedia/' + doc['title'] + '.wiki'
    if not os.path.exists(filename):
        print filename
        codecs.open(filename, 'w', 'utf-8').write(get_content(doc['title']))
