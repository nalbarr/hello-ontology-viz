help:
	@echo make run
	@echo make load-pizza-ontology

run: load-pizza-ontology

load-pizza-ontology:
	uv run -- python load_pizza_ontology.py

clean:
	rm -fr ./pizza_ontology.html
