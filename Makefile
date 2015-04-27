PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs

# Use current python binary instead of system default.
COVERAGE = python $(shell which coverage)

# Dependencies
DJANGO_VERSION ?= 1.8
NEXT_DJANGO_VERSION = $(shell python -c "v='$(DJANGO_VERSION)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")

ALCHEMY_VERSION ?= 1.0
NEXT_ALCHEMY_VERSION = $(shell python -c "v='$(ALCHEMY_VERSION)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")

MONGOENGINE_VERSION ?= 0.9
NEXT_MONGOENGINE_VERSION = $(shell python -c "v='$(MONGOENGINE_VERSION)'; parts=v.split('.'); parts[-1]=str(int(parts[-1])+1); print('.'.join(parts))")

REQ_FILE = auto_dev_requirements_django$(DJANGO_VERSION)_alchemy$(ALCHEMY_VERSION)_mongoengine$(MONGOENGINE_VERSION).txt

all: default


default:


install-deps: $(REQ_FILE)
	pip install --upgrade pip setuptools
	pip install --upgrade -r $<
	pip freeze

$(REQ_FILE): dev_requirements.txt requirements.txt
	grep --no-filename "^[^#-]" $^ | egrep -v "^(Django|SQLAlchemy|mongoengine)" > $@
	echo "Django>=$(DJANGO_VERSION),<$(NEXT_DJANGO_VERSION)" >> $@
	echo "SQLAlchemy>=$(ALCHEMY_VERSION),<$(NEXT_ALCHEMY_VERSION)" >> $@
	echo "mongoengine>=$(MONGOENGINE_VERSION),<$(NEXT_MONGOENGINE_VERSION)" >> $@


clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -path '*/__pycache__/*' -delete
	find . -type d -empty -delete
	@rm -f auto_dev_requirements_*
	@rm -rf tmp_test/


test: install-deps
	python -W default setup.py test

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
