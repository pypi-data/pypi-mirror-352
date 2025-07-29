from matplotlib.patches import PathPatch
from matplotlib.path import Path

from matplotlib_sankey._types import AcceptedColors


def patch_line(
    x_start: float,
    x_end: float,
    y1_start: float,
    y1_end: float,
    y2_start: float,
    y2_end: float,
    row_index: int,
    spacing: float = 0.0,
    alpha: float = 0.5,
    color: AcceptedColors | None = None,
) -> PathPatch:
    """Generate line patch."""
    path_patch_kwargs = {
        "color": color,
        "zorder": 0,
        "alpha": alpha,
        "lw": 0,
    }

    return PathPatch(
        Path(
            vertices=[
                (x_start, y1_start + (spacing * row_index)),
                (x_end, y1_end + (spacing * row_index)),
                (x_end, y2_start + (spacing * row_index)),
                (x_start, y2_end + (spacing * row_index)),
            ],
            codes=[Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO],
            closed=True,
        ),
        **path_patch_kwargs,
    )


def patch_curve3(
    x_start: float,
    x_end: float,
    y1_start: float,
    y1_end: float,
    y2_start: float,
    y2_end: float,
    row_index: int,
    spacing: float = 0.0,
    alpha: float = 0.5,
    color: AcceptedColors | None = None,
) -> PathPatch:
    """Generate curve3 patch."""
    path_patch_kwargs = {
        "color": color,
        "zorder": 0,
        "alpha": alpha,
        "lw": 0,
    }

    x_middle = ((x_end - x_start) / 2) + x_start

    return PathPatch(
        Path(
            vertices=[
                (x_start, y1_start + (spacing * row_index)),
                (x_middle, y1_start + (spacing * row_index)),
                (x_middle, (y1_start - y1_end) / 2 + y1_end + (spacing * row_index)),
                (x_middle, y1_end + (spacing * row_index)),
                (x_end, y1_end + (spacing * row_index)),
                (x_end, y2_start + (spacing * row_index)),
                (x_middle, y2_start + (spacing * row_index)),
                (x_middle, (y2_start - y2_end) / 2 + y2_end + (spacing * row_index)),
                (x_middle, y2_end + (spacing * row_index)),
                (x_start, y2_end + (spacing * row_index)),
            ],
            codes=[
                Path.MOVETO,
                Path.CURVE3,
                Path.CURVE3,
                Path.CURVE3,
                Path.CURVE3,
                Path.LINETO,
                Path.CURVE3,
                Path.CURVE3,
                Path.CURVE3,
                Path.CURVE3,
            ],
            closed=True,
        ),
        **path_patch_kwargs,
    )


def patch_curve4(
    x_start: float,
    x_end: float,
    y1_start: float,
    y1_end: float,
    y2_start: float,
    y2_end: float,
    row_index: int,
    spacing: float = 0.0,
    alpha: float = 0.5,
    color: AcceptedColors | None = None,
) -> PathPatch:
    """Generate curve3 patch."""
    path_patch_kwargs = {
        "color": color,
        "zorder": 0,
        "alpha": alpha,
        "lw": 0,
    }

    x_middle = ((x_end - x_start) / 2) + x_start

    return PathPatch(
        Path(
            vertices=[
                (x_start, y1_start + (spacing * row_index)),
                (x_middle, y1_start + (spacing * row_index)),
                (x_middle, y1_end + (spacing * row_index)),
                (x_end, y1_end + (spacing * row_index)),
                (x_end, y2_start + (spacing * row_index)),
                (x_middle, y2_start + (spacing * row_index)),
                (x_middle, y2_end + (spacing * row_index)),
                (x_start, y2_end + (spacing * row_index)),
            ],
            codes=[
                Path.MOVETO,
                Path.CURVE4,
                Path.CURVE4,
                Path.CURVE4,
                Path.LINETO,
                Path.CURVE4,
                Path.CURVE4,
                Path.CURVE4,
            ],
            closed=True,
        ),
        **path_patch_kwargs,
    )
