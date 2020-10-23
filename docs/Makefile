# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = CALC
SOURCEDIR     = .
BUILDDIR      = _build
DJANGODIR     = static
ROOTDIR       = ..

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

html: Makefile
# Ideally we should not have to destroy the build directory before
# rebuilding, but there appears to be a bug in either Sphinx or our
# Sphinx Theme that causes the table of contents in the sidebar
# to not be regenerated properly on all pages when it changes. So
# it's easier for now (especially since our docs build really fast) to
# wipe out the build directory between rebuilds.
	rm -rf $(BUILDDIR)

	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Note that $(DJANGODIR) might be a mounted volume, in which case it can't
# be deleted, so we'll simply delete anything *inside* it.
	rm -rf $(DJANGODIR)/*

	mkdir -p $(DJANGODIR)
	cp -R $(BUILDDIR)/html $(DJANGODIR)/docs/

# https://github.com/snide/sphinx_rtd_theme/issues/359
	sed -i.bak 's/font\/fontawesome_/fonts\/fontawesome-/g' \
	$(DJANGODIR)/docs/_static/css/badge_only.css

# Since the $(DJANGODIR) docs will be served from the user's local
# development server, we can rewrite any links to
# https://calc-dev.app.cloud.gov/ to be against the user's local
# server instead.
	sed -i.bak 's/https:\/\/calc-dev\.app\.cloud\.gov//g' \
	$(DJANGODIR)/docs/*.html

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
