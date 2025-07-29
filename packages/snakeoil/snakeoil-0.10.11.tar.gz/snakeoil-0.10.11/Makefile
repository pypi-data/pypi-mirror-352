PYTHON ?= python

SPHINX_BUILD ?= sphinx-build

.PHONY: man html
man html:
	$(SPHINX_BUILD) -a -b $@ doc build/sphinx/$@

.PHONY: sdist wheel
sdist wheel:
	$(PYTHON) -m build --$@

.PHONY: clean
clean:
	$(RM) -r build/sphinx doc/api dist

.PHONY: format
format:
	$(PYTHON) -m ruff format
