from matplotlib import colormaps
from matplotlib.colors import Colormap

from matplotlib_sankey._utils import _generate_cmap, from_matrix, isinstance_list_of, is_light_color


def test_utils_cmap() -> None:
    """Testing utils function to generate cmap."""
    assert isinstance(_generate_cmap("tab10", 4), Colormap)
    assert isinstance(_generate_cmap("viridis", 4), Colormap)
    assert _generate_cmap("viridis", 4).N == 4
    assert isinstance(_generate_cmap(["#ec4899", "#0284c7", "#16a34a", "#f59e0b"], 4), Colormap)
    assert isinstance(_generate_cmap([(0.4, 0.1, 0.9), (0.1, 0.1, 0.7)], 4), Colormap)
    assert isinstance(_generate_cmap(colormaps["tab10"], 4), Colormap)


def test_from_matrix() -> None:
    """Testing from matrix helper function."""
    assert len(from_matrix([[0, 0], [0, 0]])) == 0

    assert len(from_matrix([[0, 0], [0, 0]], source_indicies=["A", "B"], target_indicies=["C", "D"])) == 0

    assert len(from_matrix([[0, 1], [0, 0]])) == 1

    assert len(from_matrix([[0, 1], [0, 1]], source_indicies=["A", "B"], target_indicies=["C", "D"])) == 2


def test_isinstance_list_of() -> None:
    """Testing is instance list of type."""
    assert isinstance_list_of(["A", "b", "c"], str)
    assert isinstance_list_of([1, 2, 3, 4], int)
    assert isinstance_list_of(["A", "b", 1], str) is False
    assert isinstance_list_of("test", str) is False


def test_luminance() -> None:
    """Testing is light color function."""
    assert is_light_color((1, 1, 1)) is True
    assert is_light_color((0, 0, 0)) is False
    assert is_light_color((255, 255, 255), color_range_max=255) is True
