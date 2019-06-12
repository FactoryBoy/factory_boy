PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs
EXAMPLES_DIR=examples
SETUP_PY=setup.py

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)
FLAKE8 = flake8
ISORT = isort


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
	pip install --upgrade -r requirements_dev.txt
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
test:
	# imp warning is a PendingDeprecationWarning for Python 3.4 and Python 3.5
	# and a DeprecationWarning for later versions.
	# Change PendingDeprecationWarning to distutils modules when dropping
	# support for Python 3.4.
	python \
		-b \
		-Werror \
		-Wdefault:"'U' mode is deprecated":DeprecationWarning:site: \
		-Wdefault:"the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses":DeprecationWarning:distutils: \
		-Wdefault:"the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses":PendingDeprecationWarning:: \
		-Wdefault:"Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated, and in 3.8 it will stop working":DeprecationWarning:: \
		-m unittest discover

# DOC: Test the examples
example-test:
	$(MAKE) -C $(EXAMPLES_DIR) test



# Note: we run the linter in two runs, because our __init__.py files has specific warnings we want to exclude
# DOC: Perform code quality tasks
lint:
	$(FLAKE8) --config .flake8 --exclude $(PACKAGE)/__init__.py $(EXAMPLES_DIR) $(PACKAGE) $(SETUP_PY) $(TESTS_DIR)
	$(FLAKE8) --config .flake8 --ignore F401 $(PACKAGE)/__init__.py
	$(ISORT) --recursive --check-only --diff $(EXAMPLES_DIR) $(PACKAGE) $(SETUP_PY) $(TESTS_DIR)
	check-manifest

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch $(SETUP_PY) test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"


.PHONY: test testall example-test lint coverage


# Documentation
# =============


# DOC: Compile the documentation
doc:
	$(MAKE) -C $(DOC_DIR) SPHINXOPTS=-W html

linkcheck:
	$(MAKE) -C $(DOC_DIR) linkcheck

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
