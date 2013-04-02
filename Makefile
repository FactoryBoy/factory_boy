PACKAGE=factory
TESTS_DIR=tests
DOC_DIR=docs


all: default


default:


clean:
	find . -type f -name '*.pyc' -delete


test:
	python -W default setup.py test

pylint:
	pylint --rcfile=.pylintrc --report=no $(PACKAGE)/

coverage:
	coverage erase
	coverage run "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py" --branch setup.py test
	coverage report "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"
	coverage html "--include=$(PACKAGE)/*.py,$(TESTS_DIR)/*.py"

doc:
	$(MAKE) -C $(DOC_DIR) html


.PHONY: all default clean coverage doc pylint test
