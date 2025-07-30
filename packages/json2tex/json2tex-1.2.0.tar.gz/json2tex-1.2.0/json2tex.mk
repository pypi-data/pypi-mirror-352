thisdir := $(patsubst %/,%, $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

%.tex: %.json
	python $(thisdir)/json2tex.py -i $< -o $@
