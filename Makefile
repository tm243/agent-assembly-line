run:
	uvicorn agent_assembly_line.rest:app --reload

test-llm:
	python -m unittest discover -s tests/llm

test-non-llm:
	python -m unittest discover -s tests/non-llm

tests: test
test:
	python -m unittest discover -s tests/

test-verbose:
	python -m unittest discover -s tests/llm -v
	python -m unittest discover -s tests/non-llm -v

stress-test:
	@for i in {1..10}; do \
		echo "Iteration: $$i"; \
		python -m unittest discover -s tests; \
	done

build:
	python3 -m build

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +

.PHONY: test test-verbose clean
