#!/bin/sh

# try up to 3 times
./create_corpus.py || ./create_corpus.py || ./create_corpus.py

time make -j4 filter
