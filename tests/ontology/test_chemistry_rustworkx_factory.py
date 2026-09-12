import pytest

from ontology_viz.ontology.chemistry_ontology import compute_inferred_rels, get_my_ontology
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

    assert _payload_by_name(G, "PFASSubstance")["kind"] == "class"
    assert _payload_by_name(G, "PFOA")["kind"] == "individual"


@pytest.mark.slow
def test_get_stated_and_inferred_rels_adds_inferred_edge_without_duplicating_stated():
    onto = get_my_ontology()
    factory = RustworkxGraphFactory()
    G_stated = factory.get_stated_rels(onto)

    compute_inferred_rels()

    G_combined = factory.get_stated_and_inferred_rels(onto, G_stated)

    pfoa_idx = _index_by_name(G_combined, "PFOA")
    pfas_idx = _index_by_name(G_combined, "PFASSubstance")
    organofluorine_idx = _index_by_name(G_combined, "OrganofluorinePollutant")

    # Stated edge is preserved and not duplicated.
    assert len(G_combined.get_all_edge_data(pfoa_idx, pfas_idx)) == 1

    # Reasoner-inferred edge (PFOA is also an OrganofluorinePollutant) appears.
    inferred_edges = G_combined.get_all_edge_data(pfoa_idx, organofluorine_idx)
    assert len(inferred_edges) == 1
    assert inferred_edges[0]["type"] == "inferred_type"

    # G_stated itself is untouched by building the combined graph.
    stated_pfoa_idx = _index_by_name(G_stated, "PFOA")
    stated_organofluorine_idx = _index_by_name(G_stated, "OrganofluorinePollutant")
    assert not G_stated.has_edge(stated_pfoa_idx, stated_organofluorine_idx)
