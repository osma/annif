#!/usr/bin/env python3

from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import re
import os
import os.path
import time
import sys

FINTO_ENDPOINT='http://api.dev.finto.fi/sparql'
FINNA_API_SEARCH='https://api.finna.fi/v1/search'

lang = sys.argv[1]

# map ISO 639-1 language codes into the ISO 639-2 codes that Finna uses
LANGMAP = {
  'fi': 'fin',
  'sv': 'swe',
  'en': 'eng'
}

def row_to_concept(row):
    concept = {'uri': row['c']['value'],
               'pref': row['pref']['value'],
               'ysapref': row['ysapref']['value'],
               'allarspref': row['allarspref']['value']}
    if 'alts' in row:
        concept['alts'] = row['alts']['value']
    return concept

def get_concepts(lang):
    sparql = SPARQLWrapper(FINTO_ENDPOINT)
    sparql.setQuery("""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX ysometa: <http://www.yso.fi/onto/yso-meta/>

SELECT ?c ?pref (GROUP_CONCAT(?alt) AS ?alts) ?ysapref ?allarspref
WHERE {
  GRAPH <http://www.yso.fi/onto/yso/> {
    ?c a skos:Concept .
    ?c skos:prefLabel ?pref .
    FILTER(LANG(?pref)='%s')
    OPTIONAL {
      ?c skos:altLabel ?alt .
      FILTER(LANG(?alt)='%s')
    }
    FILTER NOT EXISTS { ?c owl:deprecated true }
    FILTER NOT EXISTS { ?c a ysometa:Hierarchy }
  }
  GRAPH <http://www.yso.fi/onto/ysa/> {
    ?ysac skos:closeMatch|skos:exactMatch ?c .
    ?ysac skos:prefLabel ?ysapref .
  }
  GRAPH <http://www.yso.fi/onto/allars/> {
    ?allarsc skos:closeMatch|skos:exactMatch ?c .
    ?allarsc skos:prefLabel ?allarspref .
  }
}
GROUP BY ?c ?pref ?ysapref ?allarspref
#LIMIT 500
""" % (lang, lang))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [row_to_concept(row) for row in results['results']['bindings']]
            
concepts = get_concepts(lang)

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

def generate_text(concept, lang):
    # start with pref- and altlabels
    labels = [concept['pref']]
    if lang == 'fi':
        # we can use the YSA label too
        labels.append(concept['ysapref'])
    if lang == 'sv':
        # we can use the Allars label too
        labels.append(concept['allarspref'])
    if 'alts' in concept:
        labels.append(concept['alts'])
    
    labels = ' '.join(labels)

    # look for more text in Finna API
    texts = []
    fields = ['title','summary']
    finnaterms = (concept['ysapref'], concept['allarspref'])
    finnalang = LANGMAP[lang]

    # Search type 1: exact matches using topic facet
    params = {'lookfor': 'topic_facet:"%s" OR topic_facet:"%s"' % finnaterms, 'filter[]': 'language:%s' % finnalang, 'lng':lang, 'limit':100, 'field[]':fields}
    response = search_finna(params)
    if 'records' in response:
        texts += records_to_texts(response['records'])
        
    # Search type 2: exact matches using Subject search
    params['lookfor'] = '"%s" OR "%s"' % finnaterms
    params['type'] = 'Subject'
    response = search_finna(params)
    if 'records' in response:
        texts += records_to_texts(response['records'])

    # Search type 3: fuzzy matches using Subject search
    params['lookfor'] = '(%s) OR (%s)' % finnaterms
    response = search_finna(params)
    if 'records' in response:
        texts += records_to_texts(response['records'])

    return "\n".join([labels] + list(set(texts)))

for concept in concepts:
    localname = concept['uri'].split('/')[-1]
    outfile = 'corpus/%s-%s.raw' % (localname, lang)
    if os.path.exists(outfile):
        continue

    text = None
    tries = 0
    while tries < 10:
      try:
          text = generate_text(concept, lang)
          break
      except:
          # failure, try again until tries exhausted
          tries += 1
          print("Error generating text for concept %s, trying again (attempt %d)" % (concept['uri'], tries))
          time.sleep(tries) # wait progressively longer between attempts

    if text is None:
        print("Failed looking up concept %s, exiting" % concept['uri'])
        sys.exit(1)

    print(localname, lang, concept['pref'], concept['ysapref'], concept['allarspref'], len(text.split()))
    
    f = open(outfile, 'w')
    print (concept['uri'], concept['pref'], file=f)
    print (text, file=f)
    f.close()
