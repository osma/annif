#!/usr/bin/env python3

import projects

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import glob
import re
import sys

es = Elasticsearch()
index = IndicesClient(es)

project_id = sys.argv[1]
proj = projects.AnnifProjects()[project_id]
index_name = proj.get_index_name()
analyzer = proj.get_analyzer()
corpus_pattern = proj.get_corpus_pattern()

if index.exists(index_name):
    index.delete(index_name)

indexconf = {
    'mappings': {
        'concept': {
            'properties': {
                'text': {
                    'type': 'text',
                    'analyzer': analyzer,
                    'term_vector': 'yes'
                },
                'boost': {
                    'type': 'double'
                }
            }
        }
    }
}
            
index.create(index=index_name, body=indexconf)

files = glob.glob(corpus_pattern)
for file in files:
    f = open(file, 'r')
    uri, label = f.readline().strip().split(' ', 1)
    print(file, uri, label)
    cid = uri.split('p')[-1]
    text = " ".join(f.readlines())
    text = re.sub(r'\b\d+\b', '', text) # strip words that consist of only numbers
    body = {'doc': {'uri': uri, 'label': label, 'text': text, 'boost': 1.0}, 'doc_as_upsert': True}
    es.update(index=index_name, doc_type='concept', id=cid, body=body)
    f.close()
