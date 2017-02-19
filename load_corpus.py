#!/usr/bin/env python

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import os
import re

es = Elasticsearch()
index = IndicesClient(es)

if index.exists('yso'):
    index.delete('yso')

indexconf = {
    'mappings': {
        'concept': {
            'properties': {
                'labels': {
                    'type': 'text',
                    'analyzer': 'finnish'
                },
                'text': {
                    'type': 'text',
                    'analyzer': 'finnish',
                    'term_vector': 'yes'
                },
                'boost': {
                    'type': 'double'
                }
            }
        }
    }
}
            
index.create(index='yso', body=indexconf)

files = os.listdir('corpus')
for file in files:
    if not file.endswith('.fi'):
        continue
    f = open('corpus/%s' % file, 'r')
    uri, label = f.readline().strip().split(' ', 1)
    print file, uri, label
    cid = uri.split('p')[-1]
    labels = f.readline().strip()
    text = labels + " " + "".join(f.readlines())
    text = re.sub(r'\b\d+\b', '', text) # strip words that consist of only numbers
    body = {'uri': uri, 'label': label, 'labels': labels, 'text': text, 'boost': 1}
    es.index(index='yso', doc_type='concept', id=cid, body=body)
    f.close()
