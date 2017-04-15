#!/usr/bin/env python3

import projects

from elasticsearch import Elasticsearch
import sys

es = Elasticsearch()

project_id = sys.argv[1]
uri = sys.argv[2]
localname = uri.split('p')[-1]

proj = projects.AnnifProjects()[project_id]

termvec = es.termvectors(index=proj.get_index_name(), doc_type='concept', id=localname, fields='text')

terms = []
for term,data in termvec['term_vectors']['text']['terms'].items():
    freq = data['term_freq']
    terms += freq * [term]

print(' '.join(terms))
