from collections.abc import Sequence
from typing import Any, Literal
from types import UnionType

import numpy as np
from matplotlib import colormaps
from matplotlib.axes import Axes
from matplotlib.colors import Colormap, ListedColormap

from ._types import AcceptedColors, ColorTuple


def _clean_axis(
    _ax: Axes,
    frameon: bool = True,
    reset_x_ticks: bool = True,
    reset_y_ticks: bool = True,
) -> Axes:
    """Helper function to clean axes."""
    if reset_x_ticks is True:
        _ax.set_xticklabels([])
        _ax.set_xticks([])

    if reset_y_ticks is True:
        _ax.set_yticklabels([])
        _ax.set_yticks([])
        # _ax.set_ylim(0, 1)

    if frameon is False:
        # Despine
        _ax.spines["top"].set_visible(False)
        _ax.spines["left"].set_visible(False)
        _ax.spines["right"].set_visible(False)
        _ax.spines["bottom"].set_visible(False)
    return _ax


def _generate_cmap(value: AcceptedColors, nrows: int) -> Colormap:
    """Util function to generate colormap from list of string or name."""

    def _convert_sequential_cmap_to_listed(c: Colormap, threshold: int = 256) -> Colormap:
        if c.N >= threshold:
            return ListedColormap([c(i) for i in np.linspace(start=0, stop=c.N, num=nrows).astype(int)])

        return c

    if isinstance(value, str):
        # String argument must be the name of an colormap
        assert value in list(colormaps.keys()), f"Value '{value}' is not the name of a valid colormap."

        return _convert_sequential_cmap_to_listed(colormaps.get_cmap(value))

    elif isinstance(value, Sequence):
        return ListedColormap(value)

    elif isinstance(value, Colormap):
        return _convert_sequential_cmap_to_listed(value)

    raise TypeError(f"Type '{type(value).__name__}' not allowed.")


def from_matrix(
    mtx: Sequence[Sequence[int | float]],
    source_indicies: list[int | str] | None = None,
    target_indicies: list[int | str] | None = None,
) -> Sequence[tuple[int | str, int | str, float | int]]:
    """Convert weight matrix to tuple of source, target and weight.

    Args:
        mtx (Sequence[Sequence[int | float]], optional): Weight matrix (source x target).
        source_indicies (list[int | str] | None, optional): List of source indices. Defaults to `None`.
        target_indicies (list[int | str] | None, optional): List of target indices. Defaults to `None`.

    Returns:
        List of tuples containing source, target and weight.

    ReturnType:
        list[tuple[int | str, int | str, float | int]]

    """
    # Check correct dimensions of index list
    if source_indicies is not None:
        assert len(source_indicies) == len(mtx)
    if target_indicies is not None:
        assert len(target_indicies) == len(mtx[0])

    connections = []
    for row in range(len(mtx)):
        for col in range(len(mtx[row])):
            if mtx[row][col] > 0:
                source_index: int | str = row
                target_index: int | str = col

                if source_indicies is not None:
                    source_index = source_indicies[row]
                if target_indicies is not None:
                    target_index = target_indicies[col]
                connections.append((source_index, target_index, mtx[row][col]))
    return connections


def isinstance_list_of(object: Any, dtype: type | UnionType) -> bool:
    """Check if object is list of type.

    Args:
        object (typing.Any): instance to test.
        dtype (type): Expected type of list items.

    Returns: boolean

    ReturnType: bool

    """
    if isinstance(object, list):
        return all(isinstance(x, dtype) for x in object)
    return False


def get_luminance(
    color: ColorTuple,
    color_range_max: Literal[1, 255] = 1,
) -> float:
    """Get luminance of color."""
    if color_range_max == 255:
        return (0.2126 * color[0]) / 255 + (0.7152 * color[1]) / 255 + (0.0722 * color[2]) / 255
    elif color_range_max == 1:
        return (0.2126 * color[0]) + (0.7152 * color[1]) + (0.0722 * color[2])
    else:
        raise ValueError()


def is_light_color(
    color: ColorTuple,
    color_range_max: Literal[1, 255] = 1,
    cutoff: float = 0.5,
) -> bool:
    """Check if color is light."""
    return get_luminance(color=color, color_range_max=color_range_max) > cutoff
