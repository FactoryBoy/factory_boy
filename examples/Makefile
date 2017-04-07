EXAMPLES = django_demo flask_alchemy

TEST_TARGETS = $(addprefix runtest-,$(EXAMPLES))

test: $(TEST_TARGETS)


$(TEST_TARGETS): runtest-%:
	cd $* && ./runtests.sh
