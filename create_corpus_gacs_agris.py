#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import re
import os
import os.path
import time
import sys

GACS_ENDPOINT='http://api.skosmos.dev.finto.fi/sparql'
AGRIS_ENDPOINT='http://localhost:3030/ds/sparql'

def row_to_concept(row):
    concept = {'uri': row['c']['value'],
               'pref': row['pref']['value']}
    if 'alts' in row:
        concept['alts'] = row['alts']['value']
    if 'agcs' in row:
        concept['agcs'] = row['agcs']['value']
    return concept

def get_concepts():
    sparql = SPARQLWrapper(GACS_ENDPOINT)
    sparql.setQuery("""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?c ?pref (GROUP_CONCAT(DISTINCT ?alt) AS ?alts) (GROUP_CONCAT(DISTINCT ?agc) AS ?agcs)
FROM <http://id.agrisemantics.org/gacs/>
WHERE {
    ?c a skos:Concept .
    ?c skos:prefLabel ?pref .
    FILTER(LANG(?pref)='en')
    OPTIONAL {
      ?c skos:altLabel ?alt .
      FILTER(LANG(?alt)='en')
    }
    OPTIONAL {
      ?c skos:exactMatch|skos:closeMatch|skos:narrowMatch|skos:broadMatch ?agc .
      FILTER(STRSTARTS(STR(?agc), 'http://aims.fao.org/aos/agrovoc/'))
    }
}
GROUP BY ?c ?pref
#LIMIT 10
""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [row_to_concept(row) for row in results['results']['bindings']]
            
concepts = get_concepts()

def search_agris(agc):
    sparql = SPARQLWrapper(AGRIS_ENDPOINT)
    sparql.setQuery("""
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ?title
WHERE {
    ?doc dct:subject <%s> .
    ?doc dct:title ?title .
    FILTER(LANG(?title)='eng' || LANG(?title)='en' || LANG(?title)='')
}
""" % agc)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [row['title']['value'] for row in results['results']['bindings']]    

def generate_text(concept, lang):
    # start with pref- and altlabels
    labels = [concept['pref']]
    if 'alts' in concept:
        labels.append(concept['alts'])
    
    labels = ' '.join(labels)

    # look for more text in AGRIS
    texts = []
    if 'agcs' in concept:
        for agc in concept['agcs'].split():
            texts += search_agris(agc)

    return "\n".join([labels] + list(set(texts)))

lang = 'en'
for concept in concepts:
    localname = concept['uri'].split('/')[-1]
    outfile = 'corpus/agris/%s-%s.raw' % (localname, lang)
    if os.path.exists(outfile):
        continue

    text = generate_text(concept, lang)

    if text is None:
        print("Failed looking up concept %s, exiting" % concept['uri'])
        sys.exit(1)

    print(localname, lang, concept['pref'], len(text.split()))
    
    f = open(outfile, 'w')
    print (concept['uri'], concept['pref'], file=f)
    print (text, file=f)
    f.close()
