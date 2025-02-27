test:
	python -m unittest discover -s tests

test-verbose:
	python -m unittest discover -s tests -v

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

.PHONY: test test-verbose clean