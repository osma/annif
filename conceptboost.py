#!/usr/bin/env python

from elasticsearch import Elasticsearch
import sys

def reduce_boost(uri):
    es = Elasticsearch()
    docid = uri.split('p')[-1]
    
    req = {
        'script': {
            'inline': 'ctx._source.boost = 0.8',
            'lang': 'painless'
        }
    }
    
    es.update(index='yso', doc_type='concept', id=docid, body=req)

if __name__ == '__main__':
    uri = sys.argv[1]
    reduce_boost(uri)
