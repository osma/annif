#!/usr/bin/env python3

# Perform automatic subject indexing for a directory with text files (.txt).
# If there is a .subj file, assign as many subjects as there are subjects in that file.
# Place the result in a file with the extension .asubj in TSV format.

import sys
import os
import os.path

import autoindex

dir = sys.argv[1]
for fn in os.listdir(dir):
    if not fn.lower().endswith('.txt'):
        continue
    id = fn[:-4]
    f = open(os.path.join(dir, fn))
    text = f.read()
    subjfile = os.path.join(dir, "%s.subj" % id)
    if os.path.isfile(subjfile):
        sf = open(subjfile)
        maxhits = sum(1 for line in sf)
        sf.close()
    else:
        maxhits = 3
    
    outfn = os.path.join(dir, "%s.asubj" % id)
    print(fn, len(text), subjfile, maxhits, outfn)
    
    results = autoindex.autoindex(text, 'yso-finna-fi', threshold=0.1, maxhits=maxhits)
    outfile = open(outfn, 'w')
    for result in results:
        outfile.write('<%s>\t%s\n' % (result['uri'], result['label']))
    outfile.close()
