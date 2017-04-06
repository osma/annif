#!/usr/bin/env python3

from elasticsearch import Elasticsearch
import sys

es = Elasticsearch()

lang = sys.argv[1]
uri = sys.argv[2]
localname = uri.split('p')[-1]

termvec = es.termvectors(index='yso', doc_type='concept', id=localname, fields='text_%s' % lang)

terms = []
for term,data in termvec['term_vectors']['text_%s' % lang]['terms'].items():
    freq = data['term_freq']
    terms += freq * [term]

print(' '.join(terms))
