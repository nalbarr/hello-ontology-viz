# hello-ontology-viz
hello-ontology-viz

## Ontologies

Two sample ontologies are available, selected via `ONTOLOGY_VIZ_ONTOLOGY` in `.env` (see `.env.example`):

- `pizza` (default): the classic pizza/topping ontology, inspired by `models/pizza.ttl`.
- `chemistry`: a small PFAS/chemistry ontology, inspired by `models/chemistry.ttl`. `PFOA` is stated only as a `PFASSubstance`; the reasoner infers it is also an `OrganofluorinePollutant` (has a fluorine element), demonstrating the stated vs. inferred view.

Both ontologies are hand-authored directly in owlready2 Python (`src/ontology_viz/ontology/pizza_ontology.py`, `chemistry_ontology.py`) — the `.ttl` files under `models/` are reference material, not loaded at runtime.

## Graph backends

Two graph construction/rendering backends are available, selected via `ONTOLOGY_VIZ_GRAPH_BACKEND` in `.env` (see `.env.example`):

- `networkx` (default): renders with matplotlib.
- `rustworkx`: renders with Graphviz. Requires the Graphviz `dot` binary installed on the system (e.g. `brew install graphviz` on macOS) in addition to the Python dependencies.

## Makefile targets

- `make run` / `make run-networkx` / `make run-rustworkx`: run the pizza ontology (default) with the given backend.
- `make run-chemistry` / `make run-chemistry-networkx` / `make run-chemistry-rustworkx`: run the chemistry ontology, defaulting to the `rustworkx` backend.
