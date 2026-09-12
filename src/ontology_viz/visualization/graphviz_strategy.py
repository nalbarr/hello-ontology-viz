import copy
import os

from rustworkx.visualization import graphviz_draw

from ontology_viz.visualization.base import VisualizationStrategy


def _reverse_for_layout(graph):
    """Flips child->parent edges to parent->child so dot ranks the root at the top."""
    G_layout = copy.deepcopy(graph)  # PyDiGraph.reverse() mutates in place
    G_layout.reverse()
    return G_layout


class GraphvizHierarchyStrategy(VisualizationStrategy):
    def render(self, graph, output_path: str) -> None:
        G_layout = _reverse_for_layout(graph)

        def node_attr_fn(payload):
            is_individual = payload.get("kind") == "individual"
            return {
                "label": payload["__networkx_node__"],
                "shape": "box" if is_individual else "ellipse",
                "style": "filled",
                "fillcolor": "lightyellow" if is_individual else "lavender",
            }

        def edge_attr_fn(payload):
            return {"color": payload["color"], "style": payload["style"]}

        image = graphviz_draw(
            G_layout,
            node_attr_fn=node_attr_fn,
            edge_attr_fn=edge_attr_fn,
            method="dot",
            # graph_attr values are written into the dot source without quoting
            # (unlike node_attr_fn/edge_attr_fn), so a multi-word value must be
            # pre-quoted here to remain valid Graphviz syntax.
            graph_attr={"label": '"Ontology Hierarchy (solid = stated, dashed = inferred)"', "labelloc": "b"},
        )

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        image.save(output_path)
        image.show()
