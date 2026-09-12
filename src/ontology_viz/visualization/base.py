from abc import ABC, abstractmethod

import networkx as nx


class VisualizationStrategy(ABC):
    @abstractmethod
    def render(self, graph: nx.DiGraph, output_path: str) -> None:
        """Display the graph in a window and write it to output_path."""
