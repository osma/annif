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

@functools.lru_cache(maxsize=100000)
def search(text, cutoff_frequency):
    es = Elasticsearch()

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

    return es.search(index='yso', doc_type='concept', body=query, size=40, _source=['uri','label'])

def autoindex_block(text, cutoff_frequency, limit, normalize):
    scores = {}
    res = search(text, cutoff_frequency)
    maxscore = None
    for hit in res['hits']['hits'][:limit]:
        if maxscore is None:
            maxscore = hit['_score'] # score of best hit
        uri = hit['_source']['uri']
        scores.setdefault(uri, {'uri': uri, 'label': hit['_source']['label'], 'score': 0})
        if normalize:
            scores[uri]['score'] += hit['_score'] / maxscore
        else:
            scores[uri]['score'] += 1
    
    return scores

def autoindex(text, min_block_length=15, cutoff_frequency=0.01, limit=30, normalize=True, threshold=None, maxhits=None):
    if isinstance(text, str):
        sentences = split_to_sentences(text)
    else:
        sentences = text
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
        nwords = len(block.split())
        if nwords < min_block_length:
            continue
        
        if nwords > 1000:
            # avoid too big blocks
            words = block.split()
            evalblock = ' '.join(words[:1000])
            block = ' '.join(words[1000:]) # leave this for the next iteration
        else:
            evalblock = block
            # next evaluation starts with an empty block
            block = None
            
        scores = autoindex_block(evalblock, cutoff_frequency, limit, normalize)
        # merge the results into the shared scoring dict
        for uri, hitdata in scores.items():
            if uri in all_scores:
                all_scores[uri]['score'] += hitdata['score']
            else:
                all_scores[uri] = hitdata
        
    scores = list(all_scores.values())
    scores.sort(key=lambda c:c['score'], reverse=True)
    if maxhits is not None:
        scores = scores[:maxhits]
    if len(scores) > 0 and threshold is not None:
        maxscore = scores[0]['score']
        scores = [s for s in scores if s['score'] >= maxscore * threshold]
    return scores

if __name__ == '__main__':
    text = sys.stdin.read().strip()

    scores = autoindex(split_to_sentences(text), threshold=0.2, maxhits=20)
    for c in scores[:100]:
        print(c['score'], c['uri'], c['label'])
