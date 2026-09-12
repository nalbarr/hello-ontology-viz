import pytest

from ontology_viz.ontology.pizza_ontology import compute_inferred_rels, get_my_ontology
from ontology_viz.ontology.rustworkx_factory import RustworkxGraphFactory


def _payload_by_name(graph, name):
    for payload in graph.nodes():
        if payload["__networkx_node__"] == name:
            return payload
    raise KeyError(name)


def _index_by_name(graph, name):
    for idx, payload in zip(graph.node_indices(), graph.nodes()):
        if payload["__networkx_node__"] == name:
            return idx
    raise KeyError(name)


def test_get_stated_rels_tags_node_kind():
    onto = get_my_ontology()
    G = RustworkxGraphFactory().get_stated_rels(onto)

    assert _payload_by_name(G, "MargheritaPizza")["kind"] == "class"
    assert _payload_by_name(G, "my_pizza")["kind"] == "individual"


@pytest.mark.slow
def test_get_stated_and_inferred_rels_adds_inferred_edge_without_duplicating_stated():
    onto = get_my_ontology()
    factory = RustworkxGraphFactory()
    G_stated = factory.get_stated_rels(onto)

    compute_inferred_rels()

    G_combined = factory.get_stated_and_inferred_rels(onto, G_stated)

    my_pizza_idx = _index_by_name(G_combined, "my_pizza")
    margherita_idx = _index_by_name(G_combined, "MargheritaPizza")
    cheesy_idx = _index_by_name(G_combined, "CheesyPizza")

    # Stated edge is preserved and not duplicated.
    assert len(G_combined.get_all_edge_data(my_pizza_idx, margherita_idx)) == 1

    # Reasoner-inferred edge (my_pizza is also a CheesyPizza) appears.
    inferred_edges = G_combined.get_all_edge_data(my_pizza_idx, cheesy_idx)
    assert len(inferred_edges) == 1
    assert inferred_edges[0]["type"] == "inferred_type"

    # G_stated itself is untouched by building the combined graph.
    stated_my_pizza_idx = _index_by_name(G_stated, "my_pizza")
    stated_cheesy_idx = _index_by_name(G_stated, "CheesyPizza")
    assert not G_stated.has_edge(stated_my_pizza_idx, stated_cheesy_idx)
