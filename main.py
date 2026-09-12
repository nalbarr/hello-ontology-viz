import os

from dotenv import load_dotenv

from ontology_viz.ontology import chemistry_ontology, pizza_ontology
from ontology_viz.ontology.networkx_factory import NetworkXGraphFactory
from ontology_viz.ontology.rustworkx_factory import RustworkxGraphFactory
from ontology_viz.visualization.graphviz_strategy import GraphvizHierarchyStrategy
from ontology_viz.visualization.matplotlib_strategy import MatplotlibHierarchyStrategy

load_dotenv()

ONTOLOGY_MODULES = {
    "pizza": pizza_ontology,
    "chemistry": chemistry_ontology,
}

DEFAULT_OUTPUT_PATHS = {
    "pizza": "output/pizza_ontology_hierarchy.png",
    "chemistry": "output/chemistry_ontology_hierarchy.png",
}


def main():
    ontology_name = os.getenv("ONTOLOGY_VIZ_ONTOLOGY", "pizza")
    ontology_module = ONTOLOGY_MODULES[ontology_name]

    output_path = os.getenv("ONTOLOGY_VIZ_OUTPUT_PATH", DEFAULT_OUTPUT_PATHS[ontology_name])
    backend = os.getenv("ONTOLOGY_VIZ_GRAPH_BACKEND", "networkx")

    if backend == "rustworkx":
        graph_factory = RustworkxGraphFactory()
        strategy = GraphvizHierarchyStrategy()
    else:
        graph_factory = NetworkXGraphFactory()
        strategy = MatplotlibHierarchyStrategy()

    print(f"*Load {ontology_name} ontology.")

    # 1. Setup sample ontology data
    # (Replacing with your own local file path or IRI as needed)
    onto = ontology_module.get_my_ontology()

    # 2. Extract the STATED relations
    G_stated = graph_factory.get_stated_rels(onto)

    # 3. Trigger Reasoner to compute INFERRED views
    # This calculates things like "my_pizza is a CheesyPizza" implicitly
    ontology_module.compute_inferred_rels()

    # 4. Extract BOTH relations (Highlighting differences)
    G_combined = graph_factory.get_stated_and_inferred_rels(onto, G_stated)

    # 5. Render the hierarchy tree
    strategy.render(G_combined, output_path)


if __name__ == "__main__":
    main()
