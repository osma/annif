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
                'labels': {
                    'type': 'string',
                    'analyzer': 'finnish'
                },
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
    labels = f.readline().strip()
    text = labels + " " + "".join(f.readlines())
    body = {'uri': uri, 'label': label, 'labels': labels, 'text': text, 'boost': 1}
    es.index(index='yso', doc_type='concept', id=cid, body=body)
    f.close()
