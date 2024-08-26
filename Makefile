PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs
EXAMPLES_DIR=examples
SETUP_PY=setup.py

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)
FLAKE8 = flake8
ISORT = isort
CTAGS = ctags


all: default


default:


# Package management
# ==================


# DOC: Remove temporary or compiled files
clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/


# DOC: Install and/or upgrade dependencies
update:
	pip install --upgrade pip setuptools
	pip install --upgrade --editable .[dev,doc]
	pip freeze


release:
	fullrelease


.PHONY: clean update release


# Tests and quality
# =================


# DOC: Run tests for all supported versions (creates a set of virtualenvs)
testall:
	tox

# DOC: Run tests for the currently installed version
# Remove cgi warning when dropping support for Django 3.2.
test:
	mypy --ignore-missing-imports tests/test_typing.py
	python \
		-b \
		-X dev \
		-Werror \
		-Wignore:::mongomock: \
		-Wignore:::mongomock.__version__: \
		-Wignore:::pkg_resources: \
		-m unittest

# DOC: Test the examples
example-test:
	$(MAKE) -C $(EXAMPLES_DIR) test



# Note: we run the linter in two runs, because our __init__.py files has specific warnings we want to exclude
# DOC: Perform code quality tasks
lint:
	$(FLAKE8) --exclude $(PACKAGE)/__init__.py $(EXAMPLES_DIR) $(PACKAGE) $(SETUP_PY) $(TESTS_DIR)
	$(FLAKE8) --ignore F401 $(PACKAGE)/__init__.py
	$(ISORT) --check-only --diff $(EXAMPLES_DIR) $(PACKAGE) $(SETUP_PY) $(TESTS_DIR)
	check-manifest

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run --branch -m unittest
	$(COVERAGE) report
	$(COVERAGE) html


.PHONY: test testall example-test lint coverage


# Development
# ===========

# DOC: Generate a "tags" file
TAGS:
	$(CTAGS) --recurse $(PACKAGE) $(TESTS_DIR)

.PHONY: TAGS


# Documentation
# =============


# DOC: Compile the documentation
doc:
	$(MAKE) -C $(DOC_DIR) SPHINXOPTS="-n -W" html

linkcheck:
	$(MAKE) -C $(DOC_DIR) linkcheck

spelling:
	$(MAKE) -C $(DOC_DIR) SPHINXOPTS=-W spelling

# DOC: Show this help message
help:
	@grep -A1 '^# DOC:' Makefile \
	 | awk '    					\
	    BEGIN { FS="\n"; RS="--\n"; opt_len=0; }    \
	    {    					\
		doc=$$1; name=$$2;    			\
		sub("# DOC: ", "", doc);    		\
		sub(":", "", name);    			\
		if (length(name) > opt_len) {    	\
		    opt_len = length(name)    		\
		}    					\
		opts[NR] = name;    			\
		docs[name] = doc;    			\
	    }    					\
	    END {    					\
		pat="%-" (opt_len + 4) "s %s\n";    	\
		asort(opts);    			\
		for (i in opts) {    			\
		    opt=opts[i];    			\
		    printf pat, opt, docs[opt]    	\
		}    					\
	    }'


.PHONY: doc linkcheck help
