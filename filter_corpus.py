#!/usr/bin/env python

from langdetect import detect_langs
import sys
import re

concept_info = sys.stdin.readline().strip()
print concept_info
preflabel = sys.stdin.readline().strip()
print preflabel

FINNISH = re.compile(r'\b(ja|joka|oli|kuin|jossa|jotka|jonka)\b')
SWEDISH = re.compile(r'\b(och|med|som)\b')
ENGLISH = re.compile(r'\b(and|of|for|at)\b')

def is_finnish(text):
    # Quick and dirty regex shortcuts for detecting the most common languages
    if FINNISH.search(text) is not None:
        return True
    if SWEDISH.search(text) is not None:
        return False
    if ENGLISH.search(text) is not None:
        return False
    try:
        langs = detect_langs(text)
        for lang in langs:
            if lang.lang == 'fi':
                return True
        return False
    except:
        return False


first = True
seen = set()
for line in sys.stdin.readlines():
    line = line.strip().decode('UTF-8')
    if first:
        first = False
        if line[0].lower() == line[0]: # altlabels probably
            print line.encode('UTF-8')
            continue
    if line == '':
        continue
    if line in seen:
        continue
    seen.add(line)
    if not is_finnish(line):
        continue
    print line.encode('UTF-8')
