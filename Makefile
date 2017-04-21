# Filter all corpus/*.raw files into *.txt files, stripping lines that are not in the target language

all: $(patsubst %.raw,%.txt,$(wildcard corpus/*/*.raw))

# the $(lastword ...) expression extracts the target language (e.g. "fi") from the file name
%.txt: %.raw
	./filter_corpus.py $(lastword $(subst -, ,$(@:%.txt=%))) <$^ >$@
