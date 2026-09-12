help:
	@echo make run
	@echo make test
	@echo make test-all

run:
	uv run -- python main.py

test:
	uv run -- pytest -m "not slow"

test-all:
	uv run -- pytest

clean:
	rm -fr ./pizza_ontology.html
