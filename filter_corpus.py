#!/usr/bin/env python3

from langdetect import detect_langs
import sys
import re

FINNISH = re.compile(r'\b(ja|joka|oli|kuin|jossa|jotka|jonka)\b')
SWEDISH = re.compile(r'\b(och|med|som|att|den|det|eller|av)\b')
ENGLISH = re.compile(r'\b(and|of|for|at|the)\b')

def is_in_language(targetlang, text):
    # Quick and dirty regex shortcuts for detecting the most common languages
    if FINNISH.search(text) is not None:
        return (targetlang == 'fi')
    if SWEDISH.search(text) is not None:
        return (targetlang == 'sv')
    if ENGLISH.search(text) is not None:
        return (targetlang == 'en')
    try:
        langs = detect_langs(text)
        for lang in langs:
            if lang.lang == targetlang:
                return True
        return False
    except:
        return False

seen = set()
targetlang = sys.argv[1]

# First line contains URI and preferred label, pass it through
concept_info = sys.stdin.readline().strip()
print(concept_info)
# Second line contains labels (preferred and alternate), pass them through
labels = sys.stdin.readline().strip()
print(labels)


for line in sys.stdin.readlines():
    line = line.strip()
    if line == '':
        continue
    if line in seen:
        continue
    seen.add(line)
    if not is_in_language(targetlang, line):
        continue
    print(line)
