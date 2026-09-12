import copy

import rustworkx as rx
from owlready2 import ThingClass

from ontology_viz.ontology.base import GraphFactory
from ontology_viz.ontology.networkx_factory import NetworkXGraphFactory


class RustworkxGraphFactory(GraphFactory):
    def get_stated_rels(self, onto):
        G_stated = NetworkXGraphFactory().get_stated_rels(onto)
        return rx.networkx_converter(G_stated, keep_attributes=True)

    def get_stated_and_inferred_rels(self, onto, G_stated):
        # PyDiGraph.copy() shares payload dict references with the source graph,
        # so a plain .copy() would let mutations below leak back into G_stated.
        G_combined = copy.deepcopy(G_stated)

        name_to_index = {
            payload["__networkx_node__"]: idx
            for idx, payload in zip(G_combined.node_indices(), G_combined.nodes())
        }

        def get_or_add_node(name, kind):
            if name not in name_to_index:
                name_to_index[name] = G_combined.add_node({"__networkx_node__": name, "kind": kind})
            return name_to_index[name]

        # Add inferred class structures
        for cls in onto.classes():
            for parent in cls.is_a:
                if isinstance(parent, ThingClass):
                    cls_idx = get_or_add_node(cls.name, "class")
                    parent_idx = get_or_add_node(parent.name, "class")
                    if not G_combined.has_edge(cls_idx, parent_idx):
                        G_combined.add_edge(cls_idx, parent_idx, {"type": "inferred_subClassOf", "style": "dashed", "color": "red"})

        # Add inferred individual types
        for ind in onto.individuals():
            for parent in ind.is_a:
                if isinstance(parent, ThingClass):
                    ind_idx = get_or_add_node(ind.name, "individual")
                    parent_idx = get_or_add_node(parent.name, "class")
                    if not G_combined.has_edge(ind_idx, parent_idx):
                        G_combined.add_edge(ind_idx, parent_idx, {"type": "inferred_type", "style": "dashed", "color": "orange"})

        return G_combined
