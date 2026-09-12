import os

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from ontology_viz.visualization.base import VisualizationStrategy


def _hierarchical_layout(G, root=None):
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


def _reverse_for_layout(G_combined):
    """Flips child->parent edges to parent->child so _hierarchical_layout can BFS from the root."""
    return G_combined.reverse(copy=True)


def _split_edges_by_style(G):
    """Splits edges into (solid, dashed) lists of (u, v, data) by their 'style' attribute."""
    solid_edges = []
    dashed_edges = []
    for u, v, data in G.edges(data=True):
        if data.get("style") == "dashed":
            dashed_edges.append((u, v, data))
        else:
            solid_edges.append((u, v, data))
    return solid_edges, dashed_edges


def _split_nodes_by_kind(G):
    """Splits nodes into (class_nodes, individual_nodes) by their 'kind' attribute, defaulting to class."""
    class_nodes = []
    individual_nodes = []
    for node, data in G.nodes(data=True):
        if data.get("kind", "class") == "individual":
            individual_nodes.append(node)
        else:
            class_nodes.append(node)
    return class_nodes, individual_nodes


class MatplotlibHierarchyStrategy(VisualizationStrategy):
    def render(self, graph: nx.DiGraph, output_path: str) -> None:
        G_layout = _reverse_for_layout(graph)
        pos = _hierarchical_layout(G_layout)

        class_nodes, individual_nodes = _split_nodes_by_kind(G_layout)
        solid_edges, dashed_edges = _split_edges_by_style(G_layout)

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

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        plt.savefig(output_path)
        plt.show()
