#!/usr/bin/env python3

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
            
index.create(index='yso', body=indexconf)

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
    es.update(index='yso', doc_type='concept', id=cid, body=body)
    f.close()
