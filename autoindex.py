#!/usr/bin/env python

from elasticsearch import Elasticsearch
import nltk.data
import sys
import re
import math

FINNISH = re.compile(r'\b(ja|joka|oli|kuin|jossa|jotka|jonka)\b')
SWEDISH = re.compile(r'\b(och|med|som)\b')
ENGLISH = re.compile(r'\b(and|of|for|at|the)\b')

try:
    use_labels = int(sys.argv[1])
except IndexError:
    use_labels = 0

try:
    boost_terms = float(sys.argv[2])
except IndexError:
    boost_terms = 0

try:
    minimum_should_match = int(sys.argv[3])
except IndexError:
    minimum_should_match = 20

try:
    max_doc_freq = int(sys.argv[4])
except IndexError:
    max_doc_freq = 3000

try:
    min_term_freq = int(sys.argv[5])
except IndexError:
    min_term_freq = None

try:
    min_doc_freq = int(sys.argv[6])
except IndexError:
    min_doc_freq = 3

try:
    max_query_terms = int(sys.argv[7])
except IndexError:
    max_query_terms = 1000

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
    sentences = []

    for sentence in tokenizer.tokenize(text):
        nwords = len(sentence.split())
        if not is_finnish(sentence):
            continue
        sentences.append(sentence)
    
    filteredtext = ' '.join(sentences)
    nwords = len(filteredtext.split())

    if use_labels:
        fields = ['labels','text']
    else:
        fields = ['text']
    
    global min_term_freq
    if min_term_freq is None:
        min_term_freq = int((math.log10(nwords) - 1) * 4)

    query = {
        'query': {
            'function_score': {
                'query': {
                    'more_like_this': {
                        'fields': fields,
                        'like' : filteredtext,
                        'min_term_freq': min_term_freq,
                        'min_doc_freq': min_doc_freq,
                        'max_doc_freq': max_doc_freq,
                        'max_query_terms': max_query_terms,
                        'minimum_should_match': '%d%%' % minimum_should_match,
                        'boost_terms': boost_terms
                    }
                },
                'script_score': {
                    'script': {
                        'lang': 'painless',
                        'inline': "_score * doc['boost'].value"
                    }
                }
            }
        }
    }

    limit = 40
    res = es.search(index='yso', doc_type='concept', body=query, size=limit)
    for hit in res['hits']['hits']:
        uri = hit['_source']['uri']
        scores.setdefault(uri, {'uri': uri, 'label': hit['_source']['label'], 'score': 0})
        scores[uri]['score'] += hit['_score']
    
    scores = list(scores.values())
    scores.sort(key=lambda c:c['score'], reverse=True)
    return [score for score in scores]

if __name__ == '__main__':
    text = sys.stdin.read().decode('UTF-8').strip()
    scores = autoindex(text)
    for c in scores[:40]:
        print c['score'], c['uri'], c['label'].encode('UTF-8')
