PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs
EXAMPLES_DIR=examples

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)

# Dependencies
DJANGO ?= 1.8
NEXT_DJANGO = $(shell python -c "v='$(DJANGO)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")

ALCHEMY ?= 1.0
NEXT_ALCHEMY = $(shell python -c "v='$(ALCHEMY)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")

MONGOENGINE ?= 0.9
NEXT_MONGOENGINE = $(shell python -c "v='$(MONGOENGINE)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")

REQ_FILE = auto_dev_requirements_django$(DJANGO)_alchemy$(ALCHEMY)_mongoengine$(MONGOENGINE).txt

all: default


default:


install-deps: $(REQ_FILE)
	pip install --upgrade pip setuptools
	pip install --upgrade -r $<
	pip freeze

$(REQ_FILE): dev_requirements.txt requirements.txt
	grep --no-filename "^[^#-]" $^ | egrep -v "^(Django|SQLAlchemy|mongoengine)" > $@
	echo "Django>=$(DJANGO),<$(NEXT_DJANGO)" >> $@
	echo "SQLAlchemy>=$(ALCHEMY),<$(NEXT_ALCHEMY)" >> $@
	echo "mongoengine>=$(MONGOENGINE),<$(NEXT_MONGOENGINE)" >> $@


clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -f auto_dev_requirements_*
	@rm -rf tmp_test/


test: install-deps example-test
	python -W default setup.py test

example-test:
	$(MAKE) -C $(EXAMPLES_DIR) test

pylint:
	pylint --rcfile=.pylintrc --report=no $(PACKAGE)/

coverage: install-deps
	$(COVERAGE) erase
	$(COVERAGE) run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	$(COVERAGE) report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

doc:
	$(MAKE) -C $(DOC_DIR) html


.PHONY: all default clean coverage doc install-deps pylint test
