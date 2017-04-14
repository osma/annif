#!/usr/bin/env python3

import projects

from elasticsearch import Elasticsearch
import sys

def adjust_boost(project_id, uri, factor=0.8):
    proj = projects.AnnifProjects()[project_id]
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
    
    es.update(index=proj.get_index_name(), doc_type='concept', id=docid, body=req)

if __name__ == '__main__':
    project_id = sys.argv[1]
    uri = sys.argv[2]
    adjust_boost(project_id, uri)
