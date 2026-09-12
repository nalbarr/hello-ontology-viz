from ontology_viz.ontology.networkx_factory import NetworkXGraphFactory
from ontology_viz.ontology.pizza_ontology import get_my_ontology


def test_get_stated_rels_tags_node_kind():
    onto = get_my_ontology()
    G = NetworkXGraphFactory().get_stated_rels(onto)

    assert G.nodes["MargheritaPizza"]["kind"] == "class"
    assert G.nodes["my_pizza"]["kind"] == "individual"
