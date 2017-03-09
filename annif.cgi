#!/usr/bin/env python3

import cgi
import json
import sys

import autoindex
import conceptboost

print("Content-Type: application/json")
print()

form = cgi.FieldStorage()
text = form.getfirst('text')

if text is not None:
    # autoindex mode
    results = autoindex.autoindex(text, threshold=0.2, maxhits=20)
    print(json.dumps(results))
    sys.exit()

uri = form.getfirst('uri')

if uri is not None:
    conceptboost.adjust_boost(uri)
    print('{ "status": "OK" }')
