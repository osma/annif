#!/usr/bin/env python

from elasticsearch import Elasticsearch
import sys

es = Elasticsearch()

uri = sys.argv[1]
localname = uri.split('p')[-1]

termvec = es.termvectors(index='yso', doc_type='concept', id=localname, fields='text')

terms = []
for term,data in termvec['term_vectors']['text']['terms'].items():
    freq = data['term_freq']
    terms += freq * [term]

print (' '.join(terms)).encode('UTF-8')
