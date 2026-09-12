import os

from dotenv import load_dotenv

from ontology_viz.ontology.networkx_factory import NetworkXGraphFactory
from ontology_viz.ontology.pizza_ontology import compute_inferred_rels, get_my_ontology
from ontology_viz.ontology.rustworkx_factory import RustworkxGraphFactory
from ontology_viz.visualization.graphviz_strategy import GraphvizHierarchyStrategy
from ontology_viz.visualization.matplotlib_strategy import MatplotlibHierarchyStrategy

load_dotenv()

DEFAULT_OUTPUT_PATH = "output/pizza_ontology_hierarchy.png"


def main():
    output_path = os.getenv("ONTOLOGY_VIZ_OUTPUT_PATH", DEFAULT_OUTPUT_PATH)
    backend = os.getenv("ONTOLOGY_VIZ_GRAPH_BACKEND", "networkx")

    if backend == "rustworkx":
        graph_factory = RustworkxGraphFactory()
        strategy = GraphvizHierarchyStrategy()
    else:
        graph_factory = NetworkXGraphFactory()
        strategy = MatplotlibHierarchyStrategy()

    print("*Load pizza ontology.")

    # 1. Setup sample ontology data
    # (Replacing with your own local file path or IRI as needed)
    onto = get_my_ontology()

    # 2. Extract the STATED relations
    G_stated = graph_factory.get_stated_rels(onto)

    # 3. Trigger Reasoner to compute INFERRED views
    # This calculates things like "my_pizza is a CheesyPizza" implicitly
    compute_inferred_rels()

    # 4. Extract BOTH relations (Highlighting differences)
    G_combined = graph_factory.get_stated_and_inferred_rels(onto, G_stated)

    # 5. Render the hierarchy tree
    strategy.render(G_combined, output_path)


if __name__ == "__main__":
    main()
