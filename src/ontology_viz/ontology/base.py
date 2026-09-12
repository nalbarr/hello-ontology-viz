from abc import ABC, abstractmethod


class GraphFactory(ABC):
    @abstractmethod
    def get_stated_rels(self, onto):
        """Return a stated-relations graph in this factory's native graph type."""

    @abstractmethod
    def get_stated_and_inferred_rels(self, onto, G_stated):
        """Return a combined stated+inferred graph built from G_stated (same native type)."""
