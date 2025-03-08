run:
	uvicorn src.rest:app --reload

test-async:
	python -m unittest discover -s tests/async

test-sync:
	python -m unittest discover -s tests/sync

tests: test
test:
	python -m unittest discover -s tests/

test-loaders:
	python -m unittest tests/test_data_loaders/*

test-verbose:
	python -m unittest discover -s tests/async -v
	python -m unittest discover -s tests/sync -v

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

.PHONY: test test-verbose clean
