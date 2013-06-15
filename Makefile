PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)

all: default


default:


clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -rf tmp_test/


test:
	python -W default setup.py test

pylint:
	pylint --rcfile=.pylintrc --report=no $(PACKAGE)/

coverage:
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

doc:
	$(MAKE) -C $(DOC_DIR) html


.PHONY: all default clean coverage doc pylint test
