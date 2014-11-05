test:
	cd ../../vespa && \
	python2 starter.py& \
	sleep 10 && \
	echo "Killing" $$(jobs -p) \
	trap 'kill -2 $$(jobs -p)' && \
	sleep 10 && \
	if pgrep python2; then \
		echo "Test Fail"; \
		false; \
	else \
		echo "Test OK"; \
	fi
