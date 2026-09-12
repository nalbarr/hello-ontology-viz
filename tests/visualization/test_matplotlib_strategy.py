import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from ontology_viz.visualization.matplotlib_strategy import (
    MatplotlibHierarchyStrategy,
    _hierarchical_layout,
    _reverse_for_layout,
    _split_edges_by_style,
    _split_nodes_by_kind,
)


def test_hierarchical_layout_places_root_above_children():
    G = nx.DiGraph()
    G.add_edge("A", "B")
    G.add_edge("B", "C")

    pos = _hierarchical_layout(G, root="A")

    assert set(pos.keys()) == {"A", "B", "C"}
    assert pos["A"][1] > pos["B"][1] > pos["C"][1]


def test_reverse_for_layout_flips_direction_and_keeps_attributes():
    G = nx.DiGraph()
    G.add_edge("Child", "Parent", style="solid", color="blue")
    G.nodes["Child"]["kind"] = "individual"
    G.nodes["Parent"]["kind"] = "class"

    G_layout = _reverse_for_layout(G)

    assert G_layout.has_edge("Parent", "Child")
    assert not G_layout.has_edge("Child", "Parent")
    assert G_layout["Parent"]["Child"]["style"] == "solid"
    assert G_layout["Parent"]["Child"]["color"] == "blue"
    assert G_layout.nodes["Child"]["kind"] == "individual"
    assert G_layout.nodes["Parent"]["kind"] == "class"


def test_split_edges_by_style_separates_stated_and_inferred():
    G = nx.DiGraph()
    G.add_edge("A", "B", style="solid", color="blue")
    G.add_edge("C", "D", style="solid", color="green")
    G.add_edge("E", "F", style="dashed", color="red")
    G.add_edge("G", "H", style="dashed", color="orange")

    solid_edges, dashed_edges = _split_edges_by_style(G)

    assert {(u, v) for u, v, _ in solid_edges} == {("A", "B"), ("C", "D")}
    assert {(u, v) for u, v, _ in dashed_edges} == {("E", "F"), ("G", "H")}


def test_split_nodes_by_kind_separates_classes_and_individuals():
    G = nx.DiGraph()
    G.add_node("Pizza", kind="class")
    G.add_node("my_pizza", kind="individual")
    G.add_node("Untagged")  # no kind attr, should default to class

    class_nodes, individual_nodes = _split_nodes_by_kind(G)

    assert set(class_nodes) == {"Pizza", "Untagged"}
    assert set(individual_nodes) == {"my_pizza"}


def test_matplotlib_hierarchy_strategy_render_writes_output_file(tmp_path):
    G = nx.DiGraph()
    G.add_edge("my_pizza", "MargheritaPizza", type="type", style="solid", color="green")
    G.add_edge("MargheritaPizza", "Pizza", type="subClassOf", style="solid", color="blue")
    G.add_edge("MargheritaPizza", "CheesyPizza", type="inferred_subClassOf", style="dashed", color="red")
    G.nodes["my_pizza"]["kind"] = "individual"
    G.nodes["MargheritaPizza"]["kind"] = "class"
    G.nodes["Pizza"]["kind"] = "class"
    G.nodes["CheesyPizza"]["kind"] = "class"

    output_path = tmp_path / "hierarchy.png"

    try:
        MatplotlibHierarchyStrategy().render(G, str(output_path))
    finally:
        plt.close("all")

    assert output_path.exists()
