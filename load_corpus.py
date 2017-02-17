#!/usr/bin/env python

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import os

es = Elasticsearch()
index = IndicesClient(es)

if index.exists('yso'):
    index.delete('yso')

indexconf = {
    'mappings': {
        'concept': {
            'properties': {
                'text': {
                    'type': 'string',
                    'analyzer': 'finnish'
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
    text = "".join(f.readlines())
    body = {'uri': uri, 'label': label, 'text': text}
    es.index(index='yso', doc_type='concept', id=cid, body=body)
    f.close()
