# Filter all corpus/*.txt files

all: $(patsubst %.txt,%.fi,$(wildcard corpus/*.txt))

%.fi: %.txt
	./filter_corpus.py <$^ >$@
