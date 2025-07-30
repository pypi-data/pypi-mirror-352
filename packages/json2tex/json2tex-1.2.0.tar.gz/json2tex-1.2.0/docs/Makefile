# Minimal makefile for Sphinx documentation
#
THISDIR = $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAPIDOC  = sphinx-apidoc
SPHINXPROJ    = $(shell cd .. && python3 -c 'from setuptools import find_packages;print(find_packages(exclude=["tests"])[0])')
SOURCEDIR     = source
BUILDDIR      = _build

PACKAGEDIR = $(THISDIR)/../$(SPHINXPROJ)

CHANGELOG = $(SOURCEDIR)/changelog.rst

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile apidoc $(CHANGELOG)
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: apidoc
apidoc:
	rm -f $(SOURCEDIR)/api/*.rst
	$(SPHINXAPIDOC) -M -f --separate -o "$(SOURCEDIR)/api" "$(PACKAGEDIR)"

.PHONY: $(CHANGELOG)
$(CHANGELOG):
	(echo "Changelog";echo "=========";echo) > $@
	git tag -l 'v*' -n99 --sort=-version:refname \
		--format='%(refname:strip=2) - %(contents:subject)%0a-----------------------------------------------------------------------------------------%0a%0a%(creatordate:format:%F)%0a%0a%(contents:body)' \
		>> $@
