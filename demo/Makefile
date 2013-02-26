
# You can set these variables from the command line.
SPHINXBUILD   = sphinx-build
BUILDDIR      = _build

ifeq ($(shell $(SPHINXBUILD) 2> /dev/null; echo $$?), 127)
define MSG


The 'sphinx-build' command was not found. Make sure you have Sphinx
installed, then set the SPHINXBUILD environment variable to point
to the full path of the 'sphinx-build' executable. Alternatively you
may add the Sphinx directory to PATH.

If you don't have Sphinx installed, grab it from
http://sphinx-doc.org/
endef
$(error $(MSG))
endif

html:
	$(SPHINXBUILD) -b html . $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

clean:
	-rm -rf $(BUILDDIR)

