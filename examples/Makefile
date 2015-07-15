EXAMPLES = flask_alchemy

TEST_TARGETS = $(addprefix runtest-,$(EXAMPLES))

test: $(TEST_TARGETS)


$(TEST_TARGETS): runtest-%:
	cd $* && PYTHONPATH=../.. python -m unittest
