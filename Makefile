PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs
EXAMPLES_DIR=examples

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)
FLAKE8 = flake8

all: default


default:


clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/


install-deps:
	pip install --upgrade pip setuptools
	pip install --upgrade -r requirements_dev.txt
	pip freeze

testall:
	tox

test:
	python -Wdefault -m unittest $(TESTS_DIR)

example-test:
	$(MAKE) -C $(EXAMPLES_DIR) test



# Note: we run the linter in two runs, because our __init__.py files has specific warnings we want to exclude
lint:
	check-manifest
	$(FLAKE8) --config .flake8 --exclude $(PACKAGE)/__init__.py $(PACKAGE)
	$(FLAKE8) --config .flake8 --ignore F401 $(PACKAGE)/__init__.py

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

doc:
	$(MAKE) -C $(DOC_DIR) html


.PHONY: all default clean coverage doc install-deps lint test
