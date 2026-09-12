import networkx as nx
from owlready2 import ObjectProperty, Thing, ThingClass, get_ontology, sync_reasoner
from pyvis.network import Network
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

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
                G_stated.nodes[cls.name]["kind"] = "class"
                G_stated.nodes[parent.name]["kind"] = "class"

    for ind in onto.individuals():
        for parent in ind.is_a:
            if isinstance(parent, ThingClass):
                G_stated.add_edge(ind.name, parent.name, type="type", style="solid", color="green")
                G_stated.nodes[ind.name]["kind"] = "individual"
                G_stated.nodes[parent.name]["kind"] = "class"

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

def reverse_for_layout(G_combined):
    """Flips child->parent edges to parent->child so hierarchical_layout can BFS from the root."""
    return G_combined.reverse(copy=True)


def split_edges_by_style(G):
    """Splits edges into (solid, dashed) lists of (u, v, data) by their 'style' attribute."""
    solid_edges = []
    dashed_edges = []
    for u, v, data in G.edges(data=True):
        if data.get("style") == "dashed":
            dashed_edges.append((u, v, data))
        else:
            solid_edges.append((u, v, data))
    return solid_edges, dashed_edges


def split_nodes_by_kind(G):
    """Splits nodes into (class_nodes, individual_nodes) by their 'kind' attribute, defaulting to class."""
    class_nodes = []
    individual_nodes = []
    for node, data in G.nodes(data=True):
        if data.get("kind", "class") == "individual":
            individual_nodes.append(node)
        else:
            class_nodes.append(node)
    return class_nodes, individual_nodes


def visualize_matplotlib_hierarchy(G_combined):
    G_layout = reverse_for_layout(G_combined)
    pos = hierarchical_layout(G_layout)

    class_nodes, individual_nodes = split_nodes_by_kind(G_layout)
    solid_edges, dashed_edges = split_edges_by_style(G_layout)

    plt.figure(figsize=(14, 8))

    if class_nodes:
        nx.draw_networkx_nodes(G_layout, pos, nodelist=class_nodes, node_shape="o", node_size=800, node_color="lavender")
    if individual_nodes:
        nx.draw_networkx_nodes(G_layout, pos, nodelist=individual_nodes, node_shape="s", node_size=800, node_color="lightyellow")

    if solid_edges:
        nx.draw_networkx_edges(
            G_layout, pos,
            edgelist=[(u, v) for u, v, _ in solid_edges],
            edge_color=[data["color"] for _, _, data in solid_edges],
            style="solid", arrows=True, arrowsize=12,
        )
    if dashed_edges:
        nx.draw_networkx_edges(
            G_layout, pos,
            edgelist=[(u, v) for u, v, _ in dashed_edges],
            edge_color=[data["color"] for _, _, data in dashed_edges],
            style="dashed", arrows=True, arrowsize=12,
        )

    nx.draw_networkx_labels(G_layout, pos, font_size=7)

    legend_handles = [
        Line2D([0], [0], color="blue", lw=2, linestyle="solid", label="Stated subclass"),
        Line2D([0], [0], color="green", lw=2, linestyle="solid", label="Stated type"),
        Line2D([0], [0], color="red", lw=2, linestyle="dashed", label="Inferred subclass"),
        Line2D([0], [0], color="orange", lw=2, linestyle="dashed", label="Inferred type"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="lavender", markersize=10, label="Class"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="lightyellow", markersize=10, label="Individual"),
    ]
    plt.legend(handles=legend_handles, loc="lower left", fontsize=7)

    plt.title("Ontology Hierarchy (solid = stated, dashed = inferred)")
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
    visualize_matplotlib_hierarchy(G_combined)
