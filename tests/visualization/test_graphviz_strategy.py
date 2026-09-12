import rustworkx as rx
from PIL import Image

from ontology_viz.visualization.graphviz_strategy import (
    GraphvizHierarchyStrategy,
    _reverse_for_layout,
)


def test_reverse_for_layout_flips_direction_and_keeps_payload_and_original_untouched():
    G = rx.PyDiGraph()
    child = G.add_node({"__networkx_node__": "Child", "kind": "individual"})
    parent = G.add_node({"__networkx_node__": "Parent", "kind": "class"})
    G.add_edge(child, parent, {"style": "solid", "color": "blue"})

    G_layout = _reverse_for_layout(G)

    assert G_layout.has_edge(parent, child)
    assert not G_layout.has_edge(child, parent)
    assert G_layout.get_edge_data(parent, child) == {"style": "solid", "color": "blue"}

    # Original graph is untouched (PyDiGraph.reverse() mutates in place).
    assert G.has_edge(child, parent)
    assert not G.has_edge(parent, child)


def test_graphviz_hierarchy_strategy_render_writes_output_file(tmp_path, monkeypatch):
    monkeypatch.setattr(Image.Image, "show", lambda self, *a, **kw: None)

    G = rx.PyDiGraph()
    my_pizza = G.add_node({"__networkx_node__": "my_pizza", "kind": "individual"})
    margherita = G.add_node({"__networkx_node__": "MargheritaPizza", "kind": "class"})
    pizza = G.add_node({"__networkx_node__": "Pizza", "kind": "class"})
    cheesy = G.add_node({"__networkx_node__": "CheesyPizza", "kind": "class"})
    G.add_edge(my_pizza, margherita, {"type": "type", "style": "solid", "color": "green"})
    G.add_edge(margherita, pizza, {"type": "subClassOf", "style": "solid", "color": "blue"})
    G.add_edge(margherita, cheesy, {"type": "inferred_subClassOf", "style": "dashed", "color": "red"})

    output_path = tmp_path / "hierarchy.png"

    GraphvizHierarchyStrategy().render(G, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
