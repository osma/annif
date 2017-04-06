# Filter all corpus/*.raw files into *.txt files, stripping lines that are not in the target language

all: $(patsubst %.raw,%.txt,$(wildcard corpus/*.raw))

%.txt: %.raw
	# the expression extracts the target language (e.g. "fi") from the file name
	./filter_corpus.py $(lastword $(subst -, ,$(@:%.txt=%))) <$^ >$@
