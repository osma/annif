#!/usr/bin/env python

import cgi
import json
import sys

import autoindex
import conceptboost

print "Content-Type: application/json"
print ""

form = cgi.FieldStorage()
text = form.getfirst('text')

if text is not None:
    # autoindex mode
    text = text.decode('UTF-8')

    results = autoindex.autoindex(text)
    print json.dumps(results)
    sys.exit()

uri = form.getfirst('uri')

if uri is not None:
    conceptboost.reduce_boost(uri)
    print '{ "status": "OK" }'
