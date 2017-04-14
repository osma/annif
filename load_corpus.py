#!/usr/bin/env python3

import projects

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import os
import re

es = Elasticsearch()
index = IndicesClient(es)

project_id = sys.argv[1]
proj = projects.AnnifProjects()[project_id]
index_name = proj.get_index_name()

if index.exists(index_name):
    index.delete(index_name)

indexconf = {
    'mappings': {
        'concept': {
            'properties': {
                'text_fi': {
                    'type': 'text',
                    'analyzer': 'finnish',
                    'term_vector': 'yes'
                },
                'text_sv': {
                    'type': 'text',
                    'analyzer': 'swedish',
                    'term_vector': 'yes'
                },
                'text_en': {
                    'type': 'text',
                    'analyzer': 'english',
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

files = os.listdir('corpus')
for file in files:
    match = re.match(r'.*-(\w+).txt', file)
    if not match:
        continue
    lang = match.group(1)
    f = open('corpus/%s' % file, 'r')
    uri, label = f.readline().strip().split(' ', 1)
    print(file, lang, uri, label)
    cid = uri.split('p')[-1]
    text = " ".join(f.readlines())
    text = re.sub(r'\b\d+\b', '', text) # strip words that consist of only numbers
    body = {'doc': {'uri': uri, 'label_%s' % lang: label, 'text_%s' % lang: text, 'boost': 1}, 'doc_as_upsert': True}
    es.update(index=index_name, doc_type='concept', id=cid, body=body)
    f.close()
