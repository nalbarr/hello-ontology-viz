# Chemistry Ontology (peer of Pizza)

## Goals (original)
- Given pizza ontology implementation, create a peer implementation using models/chemistry.ttl to load another ontology called chemistry_ontoloy.py
- Use same conventions for classes and inviduals loading and created stated and inferred views
- Use same approach to having two different visualization via networkx and rustworkx
- Default to rustworkx implementation
- Update tests/
- Update Makefile targets to include new chemistry ontology

## Clarified decisions

1. **`chemistry.ttl` stays reference-only, same as `pizza.ttl`.** Neither `rdflib` nor `owlready2`'s `.load()` is used anywhere today — `pizza_ontology.py` hand-authors a small illustrative subset of classes in owlready2 Python, inspired by `pizza.ttl` but not parsing it. `chemistry_ontology.py` (note: corrected filename, the goal's `chemistry_ontoloy.py` was a typo) follows the same pattern: hand-authored classes/individuals inspired by `models/chemistry.ttl`, no runtime ttl parsing.

2. **Inference demo**: `chemistry.ttl` has no `equivalent_to`/restriction construct, so nothing is available for the reasoner to infer as-is. Mirror pizza's `CheesyPizza` shape with a new class:
   ```python
   class OrganofluorinePollutant(ChemicalCompound):
       equivalent_to = [ChemicalCompound & hasElement.some(Fluorine)]
   ```
   `PFOA` is asserted only as `PFASSubstance` with `hasElement` including `Fluorine` (stated layer); the reasoner infers `PFOA` is also an `OrganofluorinePollutant` (inferred layer) — same demonstration structure as `my_pizza` / `CheesyPizza`.

3. **Ontology selection**: add a new env var `ONTOLOGY_VIZ_ONTOLOGY=pizza|chemistry` (default `pizza`) alongside the existing `ONTOLOGY_VIZ_GRAPH_BACKEND`. `main.py` picks the ontology module the same way it already picks the graph factory/strategy pair, and derives a per-ontology default output filename (e.g. `output/chemistry_ontology_hierarchy.png`).

4. **Rustworkx default is chemistry-only.** Pizza's existing default (`networkx`, via `.env.example` and `main.py`'s fallback branch) is unchanged. Only the new chemistry-specific Makefile target(s)/docs default to `rustworkx`.

## Implementation plan

### `src/ontology_viz/ontology/chemistry_ontology.py`
- New module, peer to `pizza_ontology.py`, exposing `get_my_ontology()` and reusing the existing `compute_inferred_rels()` (already ontology-agnostic — just calls `sync_reasoner()`).
- Hand-authored classes inspired by `models/chemistry.ttl`: `ChemicalCompound`, `ChemicalElement`, `ChemicalBond`, `PFASSubstance(ChemicalCompound)`, `MolecularComponent`, plus object properties `hasElement` (domain `ChemicalCompound`, range `ChemicalElement`), `hasBondType` (domain `ChemicalCompound`, range `ChemicalBond`), and `hasComponent` (domain `PFASSubstance`, range `MolecularComponent`).
  - `ChemicalBond` and `MolecularComponent` are included as full classes (not trimmed) for visual richness — they appear as extra nodes in the stated graph, and their individuals appear via type edges, even though `hasBondType`/`hasComponent` property *assertions* aren't drawn as edges by the current factories (same as pizza's `hasTopping` assertions today — see note below).
  - Datatype properties (`bondEnergyKJ`, `isPersistent`) are still skipped: owlready2 data property values (ints/bools) have no `ThingClass` parent to walk and can't render as graph nodes at all, unlike the object-property classes above.
- `OrganofluorinePollutant(ChemicalCompound)` with `equivalent_to = [ChemicalCompound & hasElement.some(Fluorine)]` — the inferred-view trigger.
- Individuals: `Fluorine` (`ChemicalElement`), `PFOA` (`PFASSubstance`), `CarbonFluorineBond` (`ChemicalBond`), `FluorinatedTail` and `CarboxylicHead` (`MolecularComponent`). Assert `PFOA.hasElement.append(Fluorine)`, `PFOA.hasBondType.append(CarbonFluorineBond)`, `PFOA.hasComponent.extend([FluorinatedTail, CarboxylicHead])` — for ontological completeness, matching `chemistry.ttl`'s `PFOA` assertions, even though the last two relations won't produce their own edges.
- **Note on visual richness**: `NetworkXGraphFactory`/`RustworkxGraphFactory` only walk `is_a` (class→parent, individual→type) — no factory code changes are in scope here. Richness comes from `ChemicalBond`/`MolecularComponent` and their individuals showing up as additional class/individual nodes (via type edges), not from `hasBondType`/`hasComponent` themselves being drawn as relationship edges.

### `main.py`
- Add `ONTOLOGY_VIZ_ONTOLOGY` env var (default `"pizza"`), select between `pizza_ontology.get_my_ontology` and `chemistry_ontology.get_my_ontology`.
- Derive `DEFAULT_OUTPUT_PATH` per ontology (`output/pizza_ontology_hierarchy.png` / `output/chemistry_ontology_hierarchy.png`) rather than a single hardcoded constant.
- Update the `print("*Load pizza ontology.")` line to reflect the selected ontology.

### `Makefile`
- New targets: `run-chemistry-networkx`, `run-chemistry-rustworkx`, and `run-chemistry` (aliased to rustworkx, matching pizza's `run: run-rustworkx` pattern but chemistry-specific).
- Update `help:` to list the new targets.

### `.env.example`
- Document `ONTOLOGY_VIZ_ONTOLOGY` alongside the existing vars; leave default backend/ontology (`networkx`/`pizza`) untouched.

### `tests/`
- Mirror the existing pizza test files rather than generalizing/parametrizing (matches "same conventions"):
  - `tests/ontology/test_chemistry_networkx_factory.py` — peer of `test_networkx_factory.py`, asserting node `kind` tagging for `PFASSubstance`/`PFOA`.
  - `tests/ontology/test_chemistry_rustworkx_factory.py` — peer of `test_rustworkx_factory.py`, including the `@pytest.mark.slow` reasoner test asserting `PFOA -> OrganofluorinePollutant` appears as `inferred_type` without duplicating the stated `PFOA -> PFASSubstance` edge, and without mutating `G_stated`.

### Docs
- Update `README.md` to mention the chemistry ontology and its Makefile targets (following the precedent set when rustworkx/graphviz was added).
