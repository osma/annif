#!/usr/bin/env python3

import cgi
import json
import sys

import autoindex
import conceptboost

DEFAULT_LANGUAGE="en"
DEFAULT_THRESHOLD=0.45
DEFAULT_MAXHITS=12

print("Content-Type: application/json")
print()

form = cgi.FieldStorage()
text = form.getfirst('text')

if text is not None:
    # autoindex mode
    
    language = form.getfirst('language')
    if language is None:
        language = DEFAULT_LANGUAGE
    
    threshold = form.getfirst('threshold')
    if threshold is not None:
        threshold = float(threshold)
    else:
        threshold = DEFAULT_THRESHOLD
    
    maxhits = form.getfirst('maxhits')
    if maxhits is not None:
        maxhits = int(maxhits)
    else:
        maxhits = DEFAULT_MAXHITS
    
    results = autoindex.autoindex(text, language, threshold=threshold, maxhits=maxhits)
    print(json.dumps(results))
    sys.exit()

uri = form.getfirst('uri')

if uri is not None:
    conceptboost.adjust_boost(uri)
    print('{ "status": "OK" }')