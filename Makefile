help:
	@echo make run
	@echo make run-networkx
	@echo make run-rustworkx
	@echo make run-chemistry
	@echo make run-chemistry-networkx
	@echo make run-chemistry-rustworkx
	@echo make test
	@echo make test-all

run: run-rustworkx

run-networkx:
	ONTOLOGY_VIZ_GRAPH_BACKEND=networkx uv run -- python main.py

run-rustworkx:
	ONTOLOGY_VIZ_GRAPH_BACKEND=rustworkx uv run -- python main.py

run-chemistry: run-chemistry-rustworkx

run-chemistry-networkx:
	ONTOLOGY_VIZ_ONTOLOGY=chemistry ONTOLOGY_VIZ_GRAPH_BACKEND=networkx uv run -- python main.py

run-chemistry-rustworkx:
	ONTOLOGY_VIZ_ONTOLOGY=chemistry ONTOLOGY_VIZ_GRAPH_BACKEND=rustworkx uv run -- python main.py

test:
	uv run -- pytest -m "not slow"

test-all:
	uv run -- pytest

clean:
	rm -fr ./output
