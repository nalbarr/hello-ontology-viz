# rustworkx Graph Backend + Graphviz Rendering

## Goals (original)
- Refactor the ontology/graph code to support a second graph library, `rustworkx`, alongside `networkx`.
- Introduce a new `ontology` package.
- Introduce a factory design pattern to return stated and inferred graphs for either `networkx` or `rustworkx`.
- References:
  - https://www.rustworkx.org/networkx.html (rustworkx vs. networkx migration notes)
  - https://www.rustworkx.org/apiref/rustworkx.visualization.graphviz_draw.html (custom visualization)

## What was built

### Package layout
```
src/ontology_viz/
  ontology/
    __init__.py
    pizza_ontology.py      # get_my_ontology(), compute_inferred_rels() — backend-agnostic
    base.py                # GraphFactory ABC
    networkx_factory.py    # NetworkXGraphFactory
    rustworkx_factory.py   # RustworkxGraphFactory
  visualization/
    __init__.py
    base.py                # VisualizationStrategy ABC (unchanged)
    matplotlib_strategy.py # MatplotlibHierarchyStrategy (unchanged, pairs with networkx)
    graphviz_strategy.py   # GraphvizHierarchyStrategy (new, pairs with rustworkx)
```
The old top-level `src/ontology_viz/pizza_ontology.py` was removed — a clean break, no back-compat shims.

### Factory design

`GraphFactory` ABC ([ontology/base.py](../src/ontology_viz/ontology/base.py)):
```python
class GraphFactory(ABC):
    def get_stated_rels(self, onto): ...
    def get_stated_and_inferred_rels(self, onto, G_stated): ...
```

Each concrete factory returns its **native** graph type — no common wrapper/adapter:
- `NetworkXGraphFactory` returns `nx.DiGraph` (today's original logic, unchanged).
- `RustworkxGraphFactory` returns `rx.PyDiGraph`.

**Design decision — how `RustworkxGraphFactory` is implemented:**
- `get_stated_rels(onto)` builds the graph via `NetworkXGraphFactory().get_stated_rels(onto)` (reusing the exact same owlready2-walking logic — no duplicated traversal code), then converts with `rustworkx.networkx_converter(G_stated, keep_attributes=True)`. This is rustworkx's own documented migration path.
- `get_stated_and_inferred_rels(onto, G_stated)` takes the **rustworkx** graph from the step above and extends it *natively* — walking `onto.classes()`/`onto.individuals()` again (same pattern as the networkx version) but using rustworkx's index-based API (`add_node`, `add_edge`, `has_edge`) instead of name-based dict access.

This hybrid was chosen over two alternatives: (a) reimplementing the whole ontology walk twice in rustworkx-native terms (more duplication, more risk of the two backends drifting), or (b) converting back and forth between networkx and rustworkx at every step (awkward, lossy). Building once via networkx+conversion, then extending natively in rustworkx space, avoids both.

### Verified rustworkx behavior (relevant since "there may not be a one-to-one mapping")
- `rx.networkx_converter(G, keep_attributes=True)`: node payload becomes `{**original_nx_node_attrs, "__networkx_node__": original_name}`; edge payload is the original edge attribute dict, unchanged. There is **no returned name→index mapping** — callers build their own by scanning `graph.nodes()` for `"__networkx_node__"`.
- `PyDiGraph.copy()` does **not** deep-copy node/edge payload dicts — they're shared references with the source graph. `RustworkxGraphFactory.get_stated_and_inferred_rels` uses `copy.deepcopy(G_stated)` instead, to avoid mutations leaking back into the caller's `G_stated`.
- `PyDiGraph` allows parallel edges by default (it's a multigraph) — `add_edge` does **not** dedupe automatically the way networkx's `add_edge(u, v, ...)` overwrites in place. The `has_edge()` guard before `add_edge()` (mirroring the networkx version's `G_combined.has_edge(...)` check) is what prevents duplicate stated/inferred edges between the same node pair.

### Rendering: `GraphvizHierarchyStrategy`

Rather than a rustworkx→matplotlib path, the rustworkx graph pairs with `rustworkx.visualization.graphviz_draw` ([visualization/graphviz_strategy.py](../src/ontology_viz/visualization/graphviz_strategy.py)):
- `method="dot"` gives hierarchical layout **for free** — no equivalent of `matplotlib_strategy.py`'s hand-rolled `_hierarchical_layout`'s BFS coordinate math is needed. It still needs its own `_reverse_for_layout`, though — see below.
- **Root-at-top requires reversing the graph, same as the matplotlib strategy.** Stored edges point child→parent (e.g. `MargheritaPizza -> Pizza`, matching "subClassOf"/"type" semantics). `dot`'s default `rankdir=TB` places an edge's tail above its head, so rendering the graph as-is put leaves at the top and the root (`Thing`) at the bottom. `matplotlib_strategy.py` already solves this by drawing the *reversed* graph (parent→child, arrowhead at the child) rather than the raw semantic direction — `graphviz_strategy.py` has its own private `_reverse_for_layout(graph)` doing the same thing (`copy.deepcopy` + `PyDiGraph.reverse()`, since `reverse()` mutates in place and edge payloads must stay intact for `edge_attr_fn`).
- `node_attr_fn`/`edge_attr_fn` callbacks receive the node/edge **payload dict** directly (not the index) and return a `dict[str, str]` of Graphviz attributes — a close match for this project's existing `kind`/`type`/`style`/`color` payload shape.
- `graphviz_draw(...)` called **without** `filename` returns a `PIL.Image`; the strategy then does `image.save(output_path)` + `image.show()`, mirroring the "write file + open window" contract of `MatplotlibHierarchyStrategy.render()`.
- **Gotcha found during implementation**: unlike `node_attr_fn`/`edge_attr_fn` values, `graph_attr` values are written into the generated dot source **without quoting**. A multi-word `graph_attr={"label": "some words"}` produces invalid Graphviz syntax and `dot` fails. Fix: pre-quote the value yourself, e.g. `{"label": '"some words"'}`.
- No direct equivalent of matplotlib's `Line2D` color-swatch legend exists in Graphviz; a `graph_attr` caption (`"Ontology Hierarchy (solid = stated, dashed = inferred)"`) is used instead.
- New dependencies: `rustworkx`, `pydot`, `pillow` (all pip-installable) plus the Graphviz `dot` **binary**, which is a system dependency `uv sync` cannot provision (documented in [README.md](../README.md); install via e.g. `brew install graphviz` on macOS).

### Backend selection

`main.py` picks a factory + matching strategy pair via `ONTOLOGY_VIZ_GRAPH_BACKEND` (`.env`, default `networkx`). The factory and strategy are coupled pairs, not independently mixable — `MatplotlibHierarchyStrategy` only understands `nx.DiGraph`, `GraphvizHierarchyStrategy` only understands `rx.PyDiGraph`:
```python
backend = os.getenv("ONTOLOGY_VIZ_GRAPH_BACKEND", "networkx")
if backend == "rustworkx":
    graph_factory, strategy = RustworkxGraphFactory(), GraphvizHierarchyStrategy()
else:
    graph_factory, strategy = NetworkXGraphFactory(), MatplotlibHierarchyStrategy()
```

### Tests
- `tests/ontology/test_networkx_factory.py` — relocated from the old `tests/test_pizza_ontology.py`, now calling `NetworkXGraphFactory().get_stated_rels(onto)`.
- `tests/ontology/test_rustworkx_factory.py` — mirrors the networkx test for `get_stated_rels`, plus a `@pytest.mark.slow` test (invokes the real HermiT reasoner via `compute_inferred_rels()`) asserting `get_stated_and_inferred_rels` adds the expected inferred edge (`my_pizza -> CheesyPizza`, type `inferred_type`) without duplicating the existing stated edge, and without mutating the input `G_stated`.
- `tests/visualization/test_graphviz_strategy.py` — builds a small `rx.PyDiGraph` by hand and asserts `GraphvizHierarchyStrategy().render(...)` writes a non-empty file; `PIL.Image.show` is monkeypatched to a no-op so the test doesn't try to open a real OS image viewer. Also covers `_reverse_for_layout` directly (edges flip direction, payload is preserved, original graph is untouched).

## Verification performed
- `uv sync` — `rustworkx`, `pydot`, `pillow` resolve cleanly.
- `uv run pytest` — all 10 tests pass (9 pass under `pytest -m "not slow"`, matching `make test`).
- `MPLBACKEND=Agg uv run python main.py` (default `networkx` backend) — unchanged behavior confirmed, writes `output/pizza_ontology_hierarchy.png`.
- `ONTOLOGY_VIZ_GRAPH_BACKEND=rustworkx uv run python main.py` — runs end-to-end, writes a valid PNG via Graphviz; visually inspected and confirmed correct (yellow boxes for individuals, lavender ellipses for classes, solid stated edges, dashed inferred edge to `CheesyPizza`, root `Thing` at the top with arrows pointing down to children — matching `MatplotlibHierarchyStrategy`'s layout convention).
