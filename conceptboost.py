#!/usr/bin/env python3

from elasticsearch import Elasticsearch
import sys

def adjust_boost(uri, factor=0.8):
    es = Elasticsearch()
    docid = uri.split('p')[-1]
    
    req = {
        'script': {
            'inline': 'ctx._source.boost *= params.factor',
            'lang': 'painless',
            'params': {
                'factor': factor
            }
        }
    }
    
    es.update(index='yso', doc_type='concept', id=docid, body=req)

if __name__ == '__main__':
    uri = sys.argv[1]
    adjust_boost(uri)
