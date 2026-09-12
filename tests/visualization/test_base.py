import pytest

from ontology_viz.visualization.base import VisualizationStrategy


def test_visualization_strategy_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        VisualizationStrategy()
