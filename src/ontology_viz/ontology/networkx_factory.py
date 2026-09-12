import networkx as nx
from owlready2 import ThingClass

from ontology_viz.ontology.base import GraphFactory


class NetworkXGraphFactory(GraphFactory):
    def get_stated_rels(self, onto):
        G_stated = nx.DiGraph()

        for cls in onto.classes():
            for parent in cls.is_a:
                if isinstance(parent, ThingClass):  # filter out complex restrictions
                    G_stated.add_edge(cls.name, parent.name, type="subClassOf", style="solid", color="blue")
                    G_stated.nodes[cls.name]["kind"] = "class"
                    G_stated.nodes[parent.name]["kind"] = "class"

        for ind in onto.individuals():
            for parent in ind.is_a:
                if isinstance(parent, ThingClass):
                    G_stated.add_edge(ind.name, parent.name, type="type", style="solid", color="green")
                    G_stated.nodes[ind.name]["kind"] = "individual"
                    G_stated.nodes[parent.name]["kind"] = "class"

        return G_stated

    def get_stated_and_inferred_rels(self, onto, G_stated):
        G_combined = G_stated.copy()

        # Add inferred class structures
        for cls in onto.classes():
            for parent in cls.is_a:
                if isinstance(parent, ThingClass):
                    if not G_combined.has_edge(cls.name, parent.name):
                        G_combined.add_edge(cls.name, parent.name, type="inferred_subClassOf", style="dashed", color="red")
                    G_combined.nodes[cls.name]["kind"] = "class"
                    G_combined.nodes[parent.name]["kind"] = "class"

        # Add inferred individual types
        for ind in onto.individuals():
            for parent in ind.is_a:
                if isinstance(parent, ThingClass):
                    if not G_combined.has_edge(ind.name, parent.name):
                        G_combined.add_edge(ind.name, parent.name, type="inferred_type", style="dashed", color="orange")
                    G_combined.nodes[ind.name]["kind"] = "individual"
                    G_combined.nodes[parent.name]["kind"] = "class"

        return G_combined
