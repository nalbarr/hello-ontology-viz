Goal:
- Refactor visualize_matplotlib_hierarchy in src/ontology_viz/pizza_ontology.py so the hierarchical tree diagram shows STATED relationships as solid lines and INFERRED relationships as dashed lines, with classes and individuals visually distinguished (comprehensive view, matching what pyvis/force-directed views already convey)
- Implement this BEFORE plans/PLAN_STANDARIZE_PYTHON_DIRS_v2.md, so v2's ontology-scale tests build on the corrected function signature/behavior

Root cause:
- visualize_matplotlib_hierarchy currently ignores G_combined (which already carries style="solid"/"dashed" and color per edge from get_stated_rels/get_stated_and_inferred_rels) and instead rebuilds its own plain graph from onto.classes()
- By the time main() calls it, the reasoner has already mutated onto's is_a lists in place, so stated vs. inferred can no longer be distinguished from onto alone
- It also silently drops individuals (e.g. my_pizza), which G_combined includes

Design decisions (confirmed):
- Individuals are included in the tree as leaves under their class (after edge reversal, e.g. MargheritaPizza -> my_pizza) rather than filtered out
- Classes vs. individuals get a node shape distinction (circle vs. square) in addition to the edge color/style distinction
- Split-by-style and graph-reversal logic are extracted into pure, unit-testable helper functions rather than left inline inside the plt-drawing function

Refactor steps:
1. Tag node kind when building graphs, so shape rendering has data to key off:
   - In get_stated_rels: when adding class/parent nodes, set kind="class" (e.g. G_stated.add_node(cls.name, kind="class")); when adding individuals, set kind="individual" on the individual node (parent class node still tagged "class")
   - In get_stated_and_inferred_rels: same tagging for any newly-added inferred nodes (most will already be tagged via the G_stated copy, but tag defensively)
2. Add reverse_for_layout(G_combined) -> G_combined.reverse(copy=True) — pure function; edge AND node attributes survive reversal, isolate this so it's independently testable
3. Add split_edges_by_style(G) -> (solid_edges, dashed_edges), each a list of (u, v, data) tuples, filtering G.edges(data=True) by data["style"]
4. Add split_nodes_by_kind(G) -> (class_nodes, individual_nodes), filtering G.nodes(data=True) by data.get("kind", "class") (default to "class" for safety if untagged)
5. Rewrite visualize_matplotlib_hierarchy(G_combined) (drop the onto param, delete the old lines 133-138 graph-rebuilding loop):
   - G_layout = reverse_for_layout(G_combined)
   - pos = hierarchical_layout(G_layout)
   - class_nodes, individual_nodes = split_nodes_by_kind(G_layout)
   - draw class_nodes with node_shape="o", individual_nodes with node_shape="s"
   - solid_edges, dashed_edges = split_edges_by_style(G_layout)  # use G_layout so arrow direction is parent->child, attrs preserved from reversal
   - draw solid_edges with style="solid" and their per-edge colors; draw dashed_edges with style="dashed" and their per-edge colors
   - add a legend (matplotlib Line2D/Patch proxies): solid blue = stated subclass, solid green = stated type, dashed red = inferred subclass, dashed orange = inferred type, circle = class, square = individual
6. Update the call site in main(): visualize_matplotlib_hierarchy(G_combined) instead of visualize_matplotlib_hierarchy(onto)

Tests to add/update in tests/test_pizza_ontology.py (none require the reasoner/Java, so none marked slow):
- test_hierarchical_layout_places_root_above_children — unchanged, still valid
- test_get_stated_rels_tags_node_kind — using get_my_ontology(), assert class nodes have kind="class" and individual nodes have kind="individual"
- test_reverse_for_layout_flips_direction_and_keeps_attributes — small synthetic graph with edge style/color and node kind attrs; assert direction is flipped and all attributes survive
- test_split_edges_by_style_separates_stated_and_inferred — synthetic graph with a mix of solid/dashed edges; assert correct partition
- test_split_nodes_by_kind_separates_classes_and_individuals — synthetic graph with mixed/missing kind attrs; assert correct partition and default-to-class fallback
- test_visualize_matplotlib_hierarchy_runs_without_error — smoke test using matplotlib.use("Agg") and a small hand-built G_combined (mixed styles, mixed kinds); assert it completes without raising

Verification:
- make run should still produce the hierarchy figure, now with visibly solid vs. dashed edges, circle vs. square nodes, and a legend
- make test (fast) should pass with the new unit tests; no new slow-marked tests needed for this plan
