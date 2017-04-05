#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import re
import os
import os.path
import time

FINTO_ENDPOINT='http://api.dev.finto.fi/sparql'
FINNA_API_SEARCH='https://api.finna.fi/v1/search'

def row_to_concept(row):
    concept = {'uri': row['c']['value'],
               'pref': row['pref']['value'],
               'ysapref': row['ysapref']['value']}
    if 'alts' in row:
        concept['alts'] = row['alts']['value']
    return concept

def get_concepts():
    sparql = SPARQLWrapper(FINTO_ENDPOINT)
    sparql.setQuery("""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX ysometa: <http://www.yso.fi/onto/yso-meta/>

SELECT ?c ?pref (GROUP_CONCAT(?alt) AS ?alts) ?ysapref
WHERE {
  GRAPH <http://www.yso.fi/onto/yso/> {
    ?c a skos:Concept .
    ?c skos:closeMatch|skos:exactMatch ?ysac .
    ?c skos:prefLabel ?pref .
    FILTER(LANG(?pref)='en')
    OPTIONAL {
      ?c skos:altLabel ?alt .
      FILTER(LANG(?alt)='en')
    }
    FILTER NOT EXISTS { ?c owl:deprecated true }
    FILTER NOT EXISTS { ?c a ysometa:Hierarchy }
  }
  GRAPH <http://www.yso.fi/onto/ysa/> {
    ?ysac skos:prefLabel ?ysapref .
  }
}
GROUP BY ?c ?pref ?ysapref
#LIMIT 500
""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [row_to_concept(row) for row in results['results']['bindings']]
            
concepts = get_concepts()

def search_finna(params):
    r = requests.get(FINNA_API_SEARCH, params=params, headers={'User-agent': 'annif 0.1'})
    return r.json()

def records_to_texts(records):
    texts = []
    for rec in records:
        if 'title' in rec:
            texts.append(rec['title'])
        if 'summary' in rec:
            for summary in rec['summary']:
                texts.append(summary)
    return texts

def generate_text(concept):
    # start with pref- and altlabels
    if 'alts' in concept:
        labels = concept['pref'] + " " + concept['alts']
    else:
        labels = concept['pref']

    # look for more text in Finna API
    texts = []
    fields = ['title','summary']

    # Search type 1: exact matches using topic facet
    params = {'lookfor': 'topic_facet:%s' % concept['ysapref'], 'filter[]': 'language:eng', 'lng':'en', 'limit':100, 'field[]':fields}
    response = search_finna(params)
    if 'records' in response:
        texts += records_to_texts(response['records'])
        
    # Search type 2: exact matches using Subject search
    params['lookfor'] = '"%s"' % concept['ysapref']
    params['type'] = 'Subject'
    response = search_finna(params)
    if 'records' in response:
        texts += records_to_texts(response['records'])

    # Search type 3: fuzzy matches using Subject search
    params['lookfor'] = concept['ysapref']
    response = search_finna(params)
    if 'records' in response:
        texts += records_to_texts(response['records'])

    return "\n".join([labels] + list(set(texts)))

for concept in concepts:
    localname = concept['uri'].split('/')[-1]
    outfile = 'corpus/%s-eng.txt' % localname
    if os.path.exists(outfile):
        continue
    try:
        text = generate_text(concept)
    except:
        # try once more
        time.sleep(1)
        text = generate_text(concept)
    print(localname, concept['pref'], concept['ysapref'], len(text.split()))
    
    f = open(outfile, 'w')
    print (concept['uri'], concept['pref'], file=f)
    print (text, file=f)
    f.close()
