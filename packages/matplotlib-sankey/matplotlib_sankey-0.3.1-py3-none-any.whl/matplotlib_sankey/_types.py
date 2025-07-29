from collections.abc import Sequence
from typing import Literal, TypeAlias

from matplotlib.colors import Colormap

CurveType: TypeAlias = Literal["curve3", "curve4", "line"]

AcceptedColors: TypeAlias = Sequence[str] | Colormap | str | Sequence[tuple[float, float, float]]

ColorTuple: TypeAlias = tuple[float, float, float, float] | tuple[float, float, float]
