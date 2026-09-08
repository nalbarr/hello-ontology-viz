import networkx as nx
from owlready2 import *
from pyvis.network import Network
import matplotlib.pyplot as plt

def hierarchical_layout(G, root=None):
    """Generates coordinates for a hierarchical tree structure."""
    pos = {}
    if root is None:
        # Find nodes with 0 in-degree (root nodes like 'Thing')
        roots = [n for n, d in G.in_degree() if d == 0]
        if not roots:
            roots = [list(G.nodes())[0]] # Fallback
    else:
        roots = [root]

    # Calculate max depths using BFS layers
    for r in roots:
        bfs_layers = list(nx.bfs_layers(G, r))
        y_step = 1.0 / max(len(bfs_layers), 1)
        
        for depth, layer in enumerate(bfs_layers):
            y_coord = 1.0 - (depth * y_step) # Top down
            x_step = 1.0 / max(len(layer), 1)
            
            for i, node in enumerate(layer):
                # Offset x slightly to center the nodes
                x_coord = (i * x_step) + (x_step / 2)
                pos[node] = (x_coord, y_coord)
    return pos


def get_my_ontology():
    onto = get_ontology("http://example.org")

    with onto:
        class Pizza(Thing): pass
        class MargheritaPizza(Pizza): pass
        class Topping(Thing): pass
        class CheeseTopping(Topping): pass

        # Define a property
        class hasTopping(ObjectProperty):
            domain = [Pizza]
            range = [Topping]

        # An inline constraint that should trigger an inference
        class CheesyPizza(Pizza):
            equivalent_to = [Pizza & hasTopping.some(CheeseTopping)]

        # Assert individual facts (Stated layer)
        my_pizza = MargheritaPizza("my_pizza")
        mozzarella = CheeseTopping("mozzarella")
        my_pizza.hasTopping.append(mozzarella)

        return onto


def get_stated_rels(onto):
    G_stated = nx.DiGraph()

    for cls in onto.classes():
        for parent in cls.is_a:
            if isinstance(parent, ThingClass):  # filter out complex restrictions
                G_stated.add_edge(cls.name, parent.name, type="subClassOf", style="solid", color="blue")

    for ind in onto.individuals():
        for parent in ind.is_a:
            if isinstance(parent, ThingClass):
                G_stated.add_edge(ind.name, parent.name, type="type", style="solid", color="green") 

    return G_stated


def compute_inferred_rels():
    sync_reasoner()


def get_stated_and_inferred_rels(onto, G_stated):
    G_combined = G_stated.copy()

    # Add inferred class structures
    for cls in onto.classes():
        for parent in cls.is_a:
            if isinstance(parent, ThingClass):
                if not G_combined.has_edge(cls.name, parent.name):
                    G_combined.add_edge(cls.name, parent.name, type="inferred_subClassOf", style="dashed", color="red")

    # Add inferred individual types
    for ind in onto.individuals():
        for parent in ind.is_a:
            if isinstance(parent, ThingClass):
                if not G_combined.has_edge(ind.name, parent.name):
                    G_combined.add_edge(ind.name, parent.name, type="inferred_type", style="dashed", color="orange")

    return G_combined


def visualize_pyvis(G_combined):
    net = Network(notebook=True, directed=True, height="500px", width="100%", cdn_resources='in_line')

    # Convert NetworkX data to Pyvis formatting
    for node in G_combined.nodes():
        net.add_node(node, label=node, title=node)

    for source, target, data in G_combined.edges(data=True):
        net.add_edge(
            source,
            target,
            title=data['type'],
            color=data['color'],
            dashes=(data['style'] == 'dashed') # Pyvis uses boolean for dashed lines
        )

    # Display network in the notebook output
    net.show("pizza_ontology.html")


def visualize_matplotlib_force_directed(G_combined):
    pos = nx.spring_layout(G_combined, k=0.15, iterations=50, seed=42)

    plt.figure(figsize=(10, 10))
    nx.draw_networkx_nodes(G_combined, pos, node_size=700, node_color="skyblue")
    nx.draw_networkx_edges(G_combined, pos, arrows=True, arrowstyle="->", arrowsize=15, edge_color="gray")
    nx.draw_networkx_labels(G_combined, pos, font_size=8, font_family="sans-serif")

    plt.title("Force-Directed Ontology Visualization")
    plt.axis("off")
    plt.show()

def visualize_matplotlib_hierarchy(onto):

    G = nx.DiGraph()
    for cls in onto.classes():
        G.add_node(cls.name)
        for parent in cls.is_a:
            if hasattr(parent, "name"):
                G.add_edge(parent.name, cls.name)

    pos = hierarchical_layout(G)

    plt.figure(figsize=(14, 8))
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color="lavender")
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=12, edge_color="darkgray")
    nx.draw_networkx_labels(G, pos, font_size=7)

    plt.title("Pure NetworkX Hierarchical Layout")
    plt.axis("off")
    plt.show()

def main():
    print("*Load pizza ontology.")

    # 1. Setup sample ontology data
    # (Replacing with your own local file path or IRI as needed)
    onto = get_my_ontology()

    # 2. Extract the STATED relations into NetworkX
    G_stated = get_stated_rels(onto)


    # 3. Trigger Reasoner to compute INFERRED views
    # This calculates things like "my_pizza is a CheesyPizza" implicitly
    compute_inferred_rels()

    # 4. Extract BOTH relations (Highlighting differences)
    G_combined = get_stated_and_inferred_rels(onto, G_stated)

    # 5a. Render Interactively with Pyvis inside the Notebook
    # visualize_pyvis(G_combined)

    # 5b. Visualize force directed
    # visualize_matplotlib_force_directed(G_combined)

    # 5c. Visualize hierarchy tree
    visualize_matplotlib_hierarchy(onto)


if __name__ == "__main__":
    main()
