EXAMPLES = django_demo flask_alchemy async

TEST_TARGETS = $(addprefix runtest-,$(EXAMPLES))

test: $(TEST_TARGETS)


$(TEST_TARGETS): runtest-%:
	cd $* && ./runtests.sh
