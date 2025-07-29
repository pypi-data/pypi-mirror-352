from typing import Any
import re
from matplotlib.colors import get_named_colors_mapping, Normalize, to_rgb

from ._utils import isinstance_list_of
from ._types import ColorTuple

from matplotlib import colormaps


def is_colormap(name: str) -> bool:
    """Check if string is name of valid colormap."""
    return name in colormaps.keys()


def is_hex_color(color: Any) -> bool:
    """Check of object is hex color string.

    Args:
        color (typing.Any): Object to check.

    Returns: boolean.

    ReturnType: bool

    """
    if isinstance(color, str):
        return re.match(r"^\#([a-f0-9A-F]{6})$", color) is not None
    return False


def is_color(color: Any) -> bool:
    """Check if value is a valid color."""
    if isinstance(color, str):
        # Check if value is hex string
        if is_hex_color(color):
            return True

        # Check if value is named color
        return color in get_named_colors_mapping().keys()
    elif isinstance(color, list | tuple | set):
        # Check if value is list|tuple of int|float
        color = list(color)

        # if len(color) == 3 or len(color) == 4:
        if len(color) == 3:
            return isinstance_list_of(color, int | float)

    return False


def colormap_to_list(
    name: str,
    num: int | None = None,
    rollover: bool = True,
    norm_vmin: int = 0,
) -> list[ColorTuple]:
    """Generate list of color tuples from cmap name."""
    assert is_colormap(name)

    cmap = colormaps.get_cmap(name)

    max_iter = cmap.N

    if num is not None:
        max_iter = num

    norm = Normalize(vmin=norm_vmin, vmax=cmap.N)

    if cmap.N == 256:
        # Norm sequencial colors
        norm = Normalize(vmin=norm_vmin, vmax=max_iter % cmap.N)

    colorlist: list[ColorTuple]

    if rollover is True:
        colorlist = [tuple(float(c) for c in cmap(norm(i % cmap.N))[:3]) for i in range(max_iter)]  # type: ignore
    else:
        colorlist = [tuple(float(c) for c in cmap(norm(i))[:3]) for i in range(max_iter)]  # type: ignore

    # assert all(len(c) == 3 for c in colorlist) or all(len(c) == 4 for c in colorlist)
    return colorlist


def unify_color(color: Any) -> ColorTuple:
    """Unify color objects to tuple of floats."""
    if isinstance(color, str):
        # Check if color is hex string
        if is_hex_color(color):
            return to_rgb(color)

        # Check if color is named matplotlib color
        # named_colors = {
        #     **colors.TABLEAU_COLORS,
        #     **colors.BASE_COLORS,
        #     **colors.CSS4_COLORS,
        #     **colors.XKCD_COLORS,
        # }
        named_colors = get_named_colors_mapping()

        if color in named_colors.keys():
            named_color_value = named_colors[color]

            # Check if named color provides hex string or float tuple
            if is_hex_color(named_color_value):
                return to_rgb(named_color_value)

            # Check if float tuple has correct format
            assert all(isinstance(i, int | float) and i >= 0 and i <= 1 for i in named_color_value)

    elif isinstance(color, list | tuple | set):
        # Check if value is list|tuple of int|float
        # color: list = list(color)

        assert len(color) == 3 or len(color) == 4
        assert isinstance_list_of(list(color), int | float)

        # if len(color) == 3:
        #     assert isinstance_list_of(color, int | float)

        #     # Check if values are between 0-255 or between 0-1
        #     if sum(color) > 3:
        #         return [c / 255 for c in color]
        return tuple(color)

    raise ValueError("Argument 'color' is invalid.")
