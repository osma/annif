#!/usr/bin/env python3

import sys
import re

import autoindex

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCTERMS, SKOS

BEGIN = re.compile(r'<doc id="(\d+)" url="([^"]+)" title="([^"]+)">')
END = '</doc>'

def autoindex_doc(text, url, title):
    g = Graph()
    uri = URIRef(url)
    g.add((uri, DCTERMS.title, Literal(title, 'fi')))
    results = autoindex.autoindex(text, 'fi', threshold=0.85, maxhits=3)
    for result in results:
        g.add((uri, DCTERMS.subject, URIRef(result['uri'])))
        g.add((URIRef(result['uri']), SKOS.prefLabel, Literal(result['label'], 'fi')))
    g.serialize(destination=sys.stdout.buffer, format='nt')

for line in sys.stdin:
    line = line.strip()

    if line == END:
        if '(täsmennyssivu)' not in title:
            autoindex_doc("\n".join(curdoc), url, title)
        continue

    m = BEGIN.match(line)
    if m is not None:
        url = m.group(2)
        title = m.group(3)
        curdoc = []
        continue

    curdoc.append(line)
             
