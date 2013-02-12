all: default


default:


clean:
	find . -type f -name '*.pyc' -delete


test:
	python -W default setup.py test

coverage:
	coverage erase
	coverage run "--include=factory/*.py,tests/*.py" --branch setup.py test
	coverage report "--include=factory/*.py,tests/*.py"
	coverage html "--include=factory/*.py,tests/*.py"


doc:
	$(MAKE) -C docs html


.PHONY: all default clean coverage doc test
