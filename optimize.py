#!/usr/bin/env python3
# hill climbing algorithm for determining optimum parameters

import os
import os.path
import sys
import random
import autoindex
import functools

# parameters and their ranges (inclusive) and step
paramdefs = {
    'min_block_length': (10,40,5),
    'cutoff_frequency': (1,22,3), # divided by 1000
    'limit': (4,40,4),
#    'normalize': (0,1,1) # converted to boolean
}

def generate_initial_params():
    # generate a random set of parameters, respecting the defined ranges
    params = {}
    for name,rangedef in paramdefs.items():
        minv, maxv, step = rangedef
        params[name] = random.randrange(minv, maxv+1, step)
    return params

def copy_and_set(d, key, val):
    """return a copy of a dict, with key set to val"""
    d2 = d.copy()
    d2[key] = val
    return d2

def param_str(params):
    if params is None:
        return '{}'
    return '{' + ', '.join(["'%s': %d" % (k, params[k]) for k in sorted(params.keys())]) + '}'

def neighbour_params(params, stepfactor):
    neighbours = []
    for name,val in params.items():
        minv, maxv, step = paramdefs[name]
        if val - (step * stepfactor) >= minv:
            neighbours.append(copy_and_set(params, name, val - (step * stepfactor)))
        if val + (step * stepfactor) <= maxv:
            neighbours.append(copy_and_set(params, name, val + (step * stepfactor)))
    return neighbours

def evaluate_document(sentences, goldlabels, name, params):
    results = autoindex.autoindex(sentences, **params)
    value = 1.0
    score = 0.0
    for res in results:
        if res['label'] in goldlabels:
            score += value
        value *= 0.9
    
    if score == 0.0:
        # tiny incentive for getting at least some results
        # to help getting away from "deserts" with zero results
        score = 0.00001 * len(results)
    
#    print(name, param_str(params), score)
    return score

def evaluate_documents(documents, params):
    score = 0.0
    for doc in documents:
        score += evaluate_document(doc['sentences'], doc['goldlabels'], doc['name'], params)
    return score    

def optimize(documents):
    curparams = bestparams = generate_initial_params()
    maxscore = evaluate_documents(documents, curparams)

    while True:
        stepped = False
        for stepfactor in range(1,10+1):
            print("current params: %s step: %d score: %s" % (param_str(curparams), stepfactor, str(maxscore)))
            print("cache info:", autoindex.search.cache_info())
            for nbparams in neighbour_params(curparams, stepfactor):
                score = evaluate_documents(documents, nbparams)
                if maxscore is None or score > maxscore:
                    bestparams = nbparams
                    print("found params: %s step: %d score: %f" % (param_str(nbparams), stepfactor, score))
                    print("cache info:", autoindex.search.cache_info())
                    maxscore = score
                    stepped = True
            if stepped:
                # already found better params, no need to step further
                curparams = bestparams
                break
        if not stepped:
            break
    
    return (curparams, maxscore)


if __name__ == '__main__':
    testdocdir = sys.argv[1]
    documents = []
    for goldfile in os.listdir(testdocdir):
        if not goldfile.endswith('.gold'):
            continue
        textfile = goldfile.replace('.gold','.txt')
        sentences = tuple(autoindex.split_to_sentences(open(os.path.join(testdocdir, textfile)).read()))
        gold = open(os.path.join(testdocdir, goldfile)).readlines()
        goldlabels = tuple([label.strip() for label in gold])
        documents.append({'sentences': sentences, 'goldlabels': goldlabels, 'name': textfile.replace('.txt','')})
        print(goldfile, len(sentences), goldlabels)

    bestparams = None
    bestscore = 0.0
    for i in range(20):
        params, score = optimize(documents)
        print("round %d params: %s score: %f" % (i, param_str(params), score))
        if score > bestscore:
            bestscore = score
            bestparams = params
    print("best params: %s score: %f" % (param_str(bestparams), bestscore))
