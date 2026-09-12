from ontology_viz.ontology.chemistry_ontology import get_my_ontology
from ontology_viz.ontology.networkx_factory import NetworkXGraphFactory


def test_get_stated_rels_tags_node_kind():
    onto = get_my_ontology()
    G = NetworkXGraphFactory().get_stated_rels(onto)

    assert G.nodes["PFASSubstance"]["kind"] == "class"
    assert G.nodes["PFOA"]["kind"] == "individual"
