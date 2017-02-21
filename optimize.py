#!/usr/bin/env python
# hill climbing algorithm for determining optimum parameters

import sys
import random
import autoindex

# parameters and their ranges (inclusive) and step
paramdefs = {
    'use_labels': (0, 1, 1),
    'boost_terms': (0, 1, 1),
    'minimum_should_match': (10,40,5),
    'max_doc_freq': (1000,8001,1000),
    'min_term_freq': (1,20,1),
    'min_doc_freq': (1,10,1),
    'max_query_terms': (100,1001,100)
}

cache = {}

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

def evaluate(text, goldlabels, params):
    global cache
    cachekey = (text, goldlabels, param_str(params))
    if cachekey in cache:
        return cache[cachekey]

    results = autoindex.autoindex(text, **params)
    value = 1.0
    score = 0.0
    for res in results:
        if res['label'] in goldlabels:
            score += value
        value *= 0.9
    cache[cachekey] = score
    return score

def optimize(text, goldlabels):
    filteredtext = autoindex.filter_text(text)

    params = generate_initial_params()
    maxscore = None

    while True:
        stepped = False
        for stepfactor in range(1,10+1):
            for nbparams in neighbour_params(params, stepfactor):
                score = evaluate(filteredtext, goldlabels, nbparams)
                if maxscore is None or score > maxscore:
                    params = nbparams
                    maxscore = score
                    stepped = True
            if stepped:
                # already found better params, no need to step further
                break
        if not stepped:
            break
    
    return (params, score)


if __name__ == '__main__':
    textfile = sys.argv[1]
    goldfile = sys.argv[2]
    text = autoindex.filter_text(open(textfile).read().decode('UTF-8'))
    gold = open(goldfile).readlines()
    goldlabels = tuple([label.strip().decode('UTF-8') for label in gold])
    print len(text), goldlabels
    bestparams = None
    bestscore = 0.0
    for i in range(10):
        params, score = optimize(text, goldlabels)
        print "round %d params: %s score: %f" % (i, param_str(params), score)
        if score > bestscore:
            bestscore = score
            bestparams = params
    print "best params: %s score: %f" % (param_str(bestparams), bestscore)
