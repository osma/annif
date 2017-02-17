#!/usr/bin/env python

from elasticsearch import Elasticsearch
import nltk.data
import sys
import re

FINNISH = re.compile(r'\b(ja|joka|oli|kuin|jossa|jotka|jonka)\b')
SWEDISH = re.compile(r'\b(och|med|som)\b')
ENGLISH = re.compile(r'\b(and|of|for|at|the)\b')

def is_finnish(text):
    # Quick and dirty regex shortcuts for detecting the most common languages
    if FINNISH.search(text) is not None:
        return True
    if SWEDISH.search(text) is not None:
        return False
    if ENGLISH.search(text) is not None:
        return False
    # assume Finnish
    return True

def autoindex(text):
    es = Elasticsearch()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') 

    scores = {}
    sentences = 0

    for sentence in tokenizer.tokenize(text):
        nwords = len(sentence.split())
        if nwords < 3:
            continue
        if not is_finnish(sentence):
            continue
        sentences += 1
        query = {
            'query': {
                'function_score': {
                    'query': {
                        'common': {
                            'text': {
                                'query': sentence,
                                'cutoff_frequency': 0.01
                            }
                        }
                    },
                    'script_score': {
                        'script': {
                            'lang': 'painless',
                            'inline': "_score * (doc['boost'].isEmpty() ? 1 : doc['boost'].value)"
                        }
                    }
                }
            }
        }

        if nwords > 20:
            limit = 20
        else:
            limit = nwords
        res = es.search(index='yso', doc_type='concept', body=query, size=limit)
        for hit in res['hits']['hits']:
            uri = hit['_source']['uri']
            scores.setdefault(uri, {'uri': uri, 'label': hit['_source']['label'], 'score': 0})
            scores[uri]['score'] += 1

    scores = list(scores.values())
    scores.sort(key=lambda c:c['score'], reverse=True)
    return [score for score in scores[:20] if score['score'] >= min(sentences / 2.0,3)]

if __name__ == '__main__':
    text = sys.stdin.read().decode('UTF-8').strip()
    scores = autoindex(text)
    for c in scores[:20]:
        print c['score'], c['uri'], c['label'].encode('UTF-8')
