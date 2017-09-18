#!/usr/bin/env python3

import sys
import csv
from bs4 import BeautifulSoup

import autoindex

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCTERMS, SKOS, XSD

def autoindex_doc(text, url, title, date, author, place):
    g = Graph()
    uri = URIRef(url)
    g.add((uri, DCTERMS.title, Literal(title, 'fi')))
    g.add((uri, DCTERMS.issued, Literal(date, datatype=XSD.date)))
    if author:
        g.add((uri, DCTERMS.creator, Literal(author, 'fi')))
    if place:
        g.add((uri, DCTERMS.spatial, Literal(place, 'fi')))
    
    results = autoindex.autoindex(text, 'yso-finna-fi', threshold=0.85, maxhits=3)
    for result in results:
        g.add((uri, DCTERMS.subject, URIRef(result['uri'])))
        g.add((URIRef(result['uri']), SKOS.prefLabel, Literal(result['label'], 'fi')))
    return g

def html_to_text(html):
    soup = BeautifulSoup(html, 'lxml')
    return soup.get_text()

reader = csv.reader(open(sys.argv[1], 'r'), delimiter='|')
for row in reader:
    id = row[0]
    title = html_to_text(row[1])
    date = row[2].strip()
    author = row[3].strip()
    place = row[4].strip()
    text = title + " " + html_to_text(row[6])
    
    url = "http://sk.example.com/%s" % id
    g = autoindex_doc(text, url, title, date, author, place)

    g.serialize(destination=sys.stdout.buffer, format='nt')

