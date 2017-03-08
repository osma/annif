#!/usr/bin/env python3
# hill climbing algorithm for determining optimum parameters

import sys
import random
import autoindex
import functools

# parameters and their ranges (inclusive) and step
paramdefs = {
    'min_block_length': (3,20,1),
    'cutoff_frequency': (1,21,5), # divided by 1000
    'limit': (4,20,4),
    'normalize': (0,1,1) # converted to boolean
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

def evaluate(sentences, goldlabels, params):
    global cache
    cachekey = (sentences, goldlabels, param_str(params))
    if cachekey in cache:
        return cache[cachekey]
    
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
    
    print((param_str(params), score))
    cache[cachekey] = score
    return score

def optimize(sentences, goldlabels):
    params = generate_initial_params()
    maxscore = None

    while True:
        stepped = False
        for stepfactor in range(1,10+1):
            for nbparams in neighbour_params(params, stepfactor):
                score = evaluate(sentences, goldlabels, nbparams)
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
    sentences = tuple(autoindex.split_to_sentences(open(textfile).read()))
    gold = open(goldfile).readlines()
    goldlabels = tuple([label.strip() for label in gold])
    print(len(sentences), goldlabels)
    bestparams = None
    bestscore = 0.0
    for i in range(20):
        params, score = optimize(sentences, goldlabels)
        print("round %d params: %s score: %f" % (i, param_str(params), score))
        if score > bestscore:
            bestscore = score
            bestparams = params
    print("best params: %s score: %f" % (param_str(bestparams), bestscore))
