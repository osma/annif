# Filter all corpus/*.txt files

all: $(patsubst %.raw,%.txt,$(wildcard corpus/*.raw))

%.txt: %.raw
	./filter_corpus.py $(lastword $(subst -, ,$(@:%.txt=%))) <$^ >$@
