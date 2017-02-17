#!/usr/bin/env python

from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import re

FINTO_ENDPOINT='http://api.dev.finto.fi/sparql'
FINNA_API_SEARCH='https://api.finna.fi/v1/search'

def row_to_concept(row):
    concept = {'uri': row['c']['value'],
               'pref': row['pref']['value']}
    if 'alts' in row:
        concept['alts'] = row['alts']['value']
    return concept

def get_concepts():
    sparql = SPARQLWrapper(FINTO_ENDPOINT)
    sparql.setQuery("""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?c ?pref (GROUP_CONCAT(?alt) AS ?alts)
FROM <http://www.yso.fi/onto/yso/>
WHERE {
  ?c a skos:Concept .
  ?c skos:prefLabel ?pref .
  FILTER(LANG(?pref)='fi')
  OPTIONAL {
    ?c skos:altLabel ?alt .
    FILTER(LANG(?alt)='fi')
  }
  FILTER NOT EXISTS { ?c owl:deprecated true }
}
GROUP BY ?c ?pref
#LIMIT 500
""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [row_to_concept(row) for row in results['results']['bindings']]
            
concepts = get_concepts()

def search_finna(params):
    r = requests.get(FINNA_API_SEARCH, params=params)
    return r.json()

def generate_text(concept):
    # start with pref- and altlabels
    if 'alts' in concept:
        texts = [concept['pref'] + " " + concept['alts']]
    else:
        texts = [concept['pref']]

    # look for more text in Finna API
    fields = ['title','summary']
    params = {'lookfor': '"%s"' % concept['pref'], 'type':'Subject', 'lng':'fi', 'limit':100, 'field[]':fields, 'headers':{'User-agent': 'annif 0.1'}}

    response = search_finna(params)
    if 'records' not in response and '(' in concept['pref']:
        # try without parenthetical qualifier
        params['lookfor'] = '"%s"' % concept['pref'].split('(')[0]
        response = search_finna(params)
    if 'records' not in response:
        # try search on all fields, not just subject
        params['type'] = 'AllFields'
        response = search_finna(params)
    if 'records' in response:
        for rec in response['records']:
            if 'title' in rec:
                texts.append(rec['title'])
            if 'summary' in rec:
                for summary in rec['summary']:
                    texts.append(summary)
    return "\n".join(texts)

for concept in concepts:
    text = generate_text(concept)
    localname = concept['uri'].split('/')[-1]
    print localname, concept['pref'].encode('UTF-8')
    f = open('corpus/%s.txt.new' % localname, 'w')
    print >>f, concept['uri'], concept['pref'].encode('UTF-8')
    print >>f, text.encode('UTF-8')
    f.close()
