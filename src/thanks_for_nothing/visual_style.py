# Copyright (c) 2026 Daniel Ari Friedman
"""Semantic plotting style and source-bound raster/vector export."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Protocol

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.image import AxesImage
from matplotlib.text import Text

mpl.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from thanks_for_nothing import __version__
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.figure_geometry import require_text_clearance, wrap_titles
from thanks_for_nothing.figure_keys import add_figure_key, draw_canvas
from thanks_for_nothing.plot_axes import PlotAxes
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.visual_tokens import LABELS, PALETTE

__all__ = [
    "DIVERGING_CMAP",
    "LABELS",
    "MIN_FONT_POINTS",
    "PALETTE",
    "PROBABILITY_CMAP",
    "PUBLICATION_FONT_POINTS",
    "PUBLICATION_WIDTH_INCHES",
    "FigureRecord",
    "PlotAxes",
    "color_scale",
    "figure",
    "panels",
    "plot_grid",
    "save",
    "shared_color_scale",
]


class _Export(Protocol):
    def savefig(
        self, fname: Path, *, dpi: float = ..., facecolor: str, metadata: dict[str, str | None]
    ) -> None: ...


class _ColorScale(Protocol):
    def colorbar(self, mappable: AxesImage, *, shrink: float, label: str) -> Colorbar: ...


def color_scale(fig: _ColorScale, image: AxesImage, label: str) -> None:
    """Attach a color scale using the image's actual owning axes."""
    _ = fig.colorbar(image, shrink=0.8, label=label)


class _SharedScale(Protocol):
    @property
    def axes(self) -> list[Axes]: ...
    def colorbar(
        self,
        mappable: AxesImage,
        *,
        ax: list[Axes],
        fraction: float,
        pad: float,
        label: str,
    ) -> Colorbar: ...


def shared_color_scale(fig: _SharedScale, image: AxesImage, label: str) -> None:
    """Bind one labeled probability scale to all axes in a matrix comparison."""
    _ = fig.colorbar(image, ax=fig.axes, fraction=0.05, pad=0.08, label=label)


def _export(fig: _Export, png: Path, svg: Path) -> None:
    fig.savefig(png, dpi=220, facecolor="white", metadata={"Software": "thanks_for_nothing"})
    fig.savefig(svg, facecolor="white", metadata={"Date": None, "Creator": "thanks_for_nothing"})


def panels(fig: Figure, *, vertical: bool = False) -> tuple[PlotAxes, PlotAxes]:
    """Create a typed pair of real axes without ndarray-returning subplot overloads."""
    rows, columns = (2, 1) if vertical else (1, 2)
    left: Axes = fig.add_subplot(rows, columns, 1)
    right: Axes = fig.add_subplot(rows, columns, 2)
    return left, right


def plot_grid(fig: Figure, layout: tuple[int, int]) -> tuple[PlotAxes, ...]:
    """Create a typed regular grid of real axes for the gaze reconstruction surfaces."""
    return tuple(fig.add_subplot(*layout, index + 1) for index in range(layout[0] * layout[1]))


MIN_FONT_POINTS: Final = 9.5
PUBLICATION_WIDTH_INCHES: Final = 6.54
PUBLICATION_FONT_POINTS: Final = 10.5
DIVERGING_CMAP: Final = "BrBG"
PROBABILITY_CMAP: Final = "cividis"
PROBABILITY_TEXT_THRESHOLD: Final = 0.5


@dataclass(frozen=True, slots=True)
class FigureRecord:
    """Published figure dimensions, legibility and immutable source/image digests."""

    name: str
    title: str
    alt: str
    source_artifacts: tuple[str, ...]
    source_sha256: tuple[str, ...]
    png_sha256: str
    svg_sha256: str
    width_inches: float
    height_inches: float
    min_font_points: float
    publication_min_font_points: float
    legend_labels: tuple[str, ...]


def figure(
    width: float = 6.54, height: float = 4.2, *, automatic_layout: bool = True
) -> tuple[Figure, PlotAxes]:
    """Create a constrained-layout Agg figure with readable semantic defaults."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.titlepad": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.axisbelow": True,
            "grid.color": PALETTE["grid"],
            "grid.linewidth": 0.6,
            "lines.linewidth": 1.7,
            "lines.markersize": 5,
            "legend.frameon": False,
            "legend.handlelength": 1.8,
            "legend.labelspacing": 0.65,
            "legend.columnspacing": 1.4,
            "axes.labelpad": 7,
            "axes.linewidth": 0.8,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.color": PALETTE["ink"],
            "ytick.color": PALETTE["ink"],
            "errorbar.capsize": 3,
            "figure.constrained_layout.w_pad": 0.07,
            "figure.constrained_layout.h_pad": 0.09,
            "figure.constrained_layout.wspace": 0.08,
            "figure.constrained_layout.hspace": 0.08,
            "axes.labelcolor": PALETTE["ink"],
            "text.color": PALETTE["ink"],
            "axes.edgecolor": PALETTE["ink"],
            "svg.fonttype": "none",
            "svg.hashsalt": f"thanks_for_nothing-{__version__}",
        }
    )
    fig, ax = plt.subplots(
        figsize=(width, 1.1 * height), layout="constrained" if automatic_layout else "none"
    )
    if not automatic_layout:
        fig.subplots_adjust(left=0.04, right=0.98, bottom=0.04, top=0.95, wspace=0.22, hspace=0.22)
    return fig, ax


def save(  # noqa: PLR0913, PLR0917 - Preserve the shared export API.
    fig: Figure,
    output: Path,
    name: str,
    title: str,
    alt: str,
    sources: tuple[str, ...],
) -> FigureRecord:
    """Bind both rendered formats to nonempty sources and enforce minimum text size."""
    try:
        if not sources or any((output.parent / source).stat().st_size == 0 for source in sources):
            message = "Figure sources must exist and contain data"
            raise ContractError(message)
        source_hashes = tuple(file_digest(output.parent / source) for source in sources)
        draw_canvas(fig.canvas)
        sizes = [
            float(artist.get_fontsize())
            for artist in fig.findobj()
            if isinstance(artist, Text) and artist.get_text() and artist.get_visible()
        ]
        if not sizes or min(sizes) < MIN_FONT_POINTS:
            message = "Figure text must be present and at least 9.5 points"
            raise ContractError(message)
        scale = max(1.0, fig.get_figwidth() / PUBLICATION_WIDTH_INCHES)
        for artist in fig.findobj():
            if isinstance(artist, Text) and artist.get_text() and artist.get_visible():
                artist.set_fontsize(max(float(artist.get_fontsize()), PUBLICATION_FONT_POINTS * scale))
        wrap_titles(fig)
        legend_labels = add_figure_key(fig, name, PUBLICATION_FONT_POINTS * scale)
        draw_canvas(fig.canvas)
        require_text_clearance(fig)
        sizes = [
            float(artist.get_fontsize())
            for artist in fig.findobj()
            if isinstance(artist, Text) and artist.get_text() and artist.get_visible()
        ]
        output.mkdir(parents=True, exist_ok=True)
        png, svg = output / f"{name}.png", output / f"{name}.svg"
        _export(fig, png, svg)
        return FigureRecord(
            name,
            title,
            alt,
            sources,
            source_hashes,
            file_digest(png),
            file_digest(svg),
            fig.get_figwidth(),
            fig.get_figheight(),
            min(sizes),
            min(sizes) / scale,
            legend_labels,
        )
    finally:
        plt.close(fig)
