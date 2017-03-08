#!/usr/bin/env python3

from elasticsearch import Elasticsearch
import nltk.data
import sys
import re
import math
import functools

FINNISH = re.compile(r'\b(ja|joka|oli|kuin|jossa|jotka|jonka)\b')
SWEDISH = re.compile(r'\b(och|med|som|att|den|det|eller|av)\b')
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

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') 
def split_to_sentences(text):
    sentences = []
    for sentence in sentence_tokenizer.tokenize(text):
        if not is_finnish(sentence):
            continue
        sentences.append(sentence)
    return sentences

@functools.lru_cache(maxsize=None)
def autoindex_block(text, cutoff_frequency, limit, normalize):
    es = Elasticsearch()
    scores = {}

    query = {
        'query': {
            'function_score': {
                'query': {
                    'common': {
                        'text': {
                            'query': text,
                            'cutoff_frequency': cutoff_frequency
                        }
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

    res = es.search(index='yso', doc_type='concept', body=query, size=limit)
    maxscore = None
    for hit in res['hits']['hits']:
        if maxscore is None:
            maxscore = hit['_score'] # score of best hit
        uri = hit['_source']['uri']
        scores.setdefault(uri, {'uri': uri, 'label': hit['_source']['label'], 'score': 0})
        if normalize:
            scores[uri]['score'] += hit['_score'] / maxscore
        else:
            scores[uri]['score'] += 1
    
    return scores

def autoindex(sentences, min_block_length, cutoff_frequency, limit, normalize):
    all_scores = {}
    
    # allow integer values representing thousands
    if cutoff_frequency >= 1.0:
        cutoff_frequency *= 0.001

    block = None
    for sentence in sentences:
        if block is None:
            block = sentence
        else:
            block = block + " " + sentence
        if len(block.split()) < min_block_length:
            continue
        scores = autoindex_block(block, cutoff_frequency, limit, normalize)
        # merge the results into the shared scoring dict
        for uri, hitdata in scores.items():
            if uri in all_scores:
                all_scores[uri]['score'] += hitdata['score']
            else:
                all_scores[uri] = hitdata
        
    scores = list(all_scores.values())
    scores.sort(key=lambda c:c['score'], reverse=True)
    return [score for score in scores]


if __name__ == '__main__':
    text = sys.stdin.read().strip()

    scores = autoindex(split_to_sentences(text), min_block_length=5, cutoff_frequency=0.01, limit=10, normalize=True)
    for c in scores[:100]:
        print(c['score'], c['uri'], c['label'])
