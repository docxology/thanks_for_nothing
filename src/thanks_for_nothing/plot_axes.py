# Copyright (c) 2026 Daniel Ari Friedman
"""The consumed structural Matplotlib interface, separate from runtime visual style."""

from collections.abc import Sequence
from typing import Literal, Protocol, TypeAlias, TypedDict, Unpack

import numpy as np
from matplotlib.artist import Artist
from matplotlib.axis import Tick, XAxis, YAxis
from matplotlib.collections import FillBetweenPolyCollection
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.image import AxesImage
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text
from matplotlib.transforms import Transform
from numpy.typing import NDArray

_Numbers = float | Sequence[float] | NDArray[np.float64] | NDArray[np.int64]
_Errors = Sequence[Sequence[float]] | Sequence[NDArray[np.float64]] | None


class _AxisSettings(TypedDict, total=False):
    xlim: tuple[float | None, float | None]
    ylim: tuple[float | None, float | None]
    xlabel: str
    ylabel: str
    title: str
    yscale: Literal["linear", "log"]
    xscale: Literal["linear", "log"]


class _PlotAxes(Protocol):
    """Consumed Matplotlib methods, retaining concrete artist return types.

    Matplotlib's bundled annotations leave these keyword arguments unknown.
    Actual Axes objects must structurally satisfy this narrow plotting contract.
    """

    transAxes: Transform  # noqa: N815 - Exact Matplotlib public attribute.
    xaxis: XAxis
    yaxis: YAxis

    def set(self, **kwargs: Unpack[_AxisSettings]) -> list[Artist]: ...
    def axis(self, arg: Literal["off"], /) -> tuple[float, float, float, float]: ...
    def add_patch(self, patch: Patch, /) -> Patch: ...
    def text(  # noqa: PLR0913 - Exact consumed Matplotlib signature.
        self,
        x: float,
        y: float,
        s: str,
        *,
        fontsize: float = ...,
        weight: str = ...,
        va: str = ...,
        ha: str = ...,
        linespacing: float = ...,
        transform: Transform | None = ...,
        color: str = ...,
    ) -> Text: ...
    def bar(  # noqa: PLR0913 - Exact consumed Matplotlib signature.
        self,
        x: _Numbers,
        height: _Numbers,
        *,
        width: float = ...,
        bottom: _Numbers | None = ...,
        color: str = ...,
        hatch: str = ...,
        edgecolor: str = ...,
        linewidth: float = ...,
        label: str = ...,
    ) -> BarContainer: ...
    def set_xticks(self, ticks: _Numbers, labels: Sequence[str]) -> list[Tick]: ...
    def set_yticks(self, ticks: _Numbers, labels: Sequence[str]) -> list[Tick]: ...
    def legend(
        self,
        *,
        loc: Literal[
            "upper right", "upper center", "lower left", "lower center", "center right", "center"
        ] = ...,
        ncol: int = ...,
    ) -> Legend: ...
    def plot(  # noqa: PLR0913 - Exact consumed Matplotlib signature.
        self,
        x: _Numbers,
        y: _Numbers,
        fmt: str = ...,
        *,
        color: str = ...,
        linestyle: str = ...,
        label: str = ...,
        linewidth: float = ...,
        markersize: float = ...,
        alpha: float = ...,
    ) -> list[Line2D]: ...
    def axvline(
        self,
        x: float,
        *,
        color: str,
        lw: float = ...,
        linestyle: str = ...,
        label: str = ...,
    ) -> Line2D: ...
    def axhline(
        self, y: float, *, color: str, linestyle: str = ..., lw: float = ..., label: str = ...
    ) -> Line2D: ...
    def fill_between(
        self, x: _Numbers, y1: _Numbers, y2: _Numbers, *, color: str, alpha: float
    ) -> FillBetweenPolyCollection: ...
    def errorbar(  # noqa: PLR0913 - Exact consumed Matplotlib signature.
        self,
        x: _Numbers,
        y: _Numbers,
        *,
        xerr: _Errors = ...,
        yerr: _Errors = ...,
        fmt: str,
        capsize: float,
        color: str,
        label: str = ...,
    ) -> ErrorbarContainer: ...
    def invert_yaxis(self) -> None: ...
    def imshow(  # noqa: PLR0913 - Exact consumed Matplotlib signature.
        self,
        values: NDArray[np.float64],
        /,
        *,
        cmap: str | None = ...,
        vmin: float | None = ...,
        vmax: float | None = ...,
        aspect: Literal["auto", "equal"] = ...,
        extent: tuple[float, float, float, float] | None = ...,
    ) -> AxesImage: ...


PlotAxes: TypeAlias = _PlotAxes
