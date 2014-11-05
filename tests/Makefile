MAKE=make
SUBDIRS=test-destroy
.PHONY:	tests test $(SUBDIRS)

tests: $(addprefix test-,$(SUBDIRS))

test-%:
	echo "Running test in $*"
	$(MAKE) --directory=$* test
