# hello-ontology-viz
hello-ontology-viz

## Graph backends

Two graph construction/rendering backends are available, selected via `ONTOLOGY_VIZ_GRAPH_BACKEND` in `.env` (see `.env.example`):

- `networkx` (default): renders with matplotlib.
- `rustworkx`: renders with Graphviz. Requires the Graphviz `dot` binary installed on the system (e.g. `brew install graphviz` on macOS) in addition to the Python dependencies.
