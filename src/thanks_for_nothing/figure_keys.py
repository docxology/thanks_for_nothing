# Copyright (c) 2026 Daniel Ari Friedman
"""Visible, source-recorded legend footers without shrinking the scientific panels."""

from textwrap import fill
from typing import Literal, Protocol, assert_never

import matplotlib.patheffects as effects
from matplotlib.artist import Artist
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Text

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.legend_entries import EXTRA_KEYS, KeyGlyph
from thanks_for_nothing.visual_tokens import PALETTE


class _KeyAxes(Protocol):
    def get_legend_handles_labels(self) -> tuple[list[Artist], list[str]]: ...
    def get_legend(self) -> Legend | None: ...


class _Canvas(Protocol):
    def draw(self) -> None: ...


class _LayoutFigure(Protocol):
    def set_layout_engine(self, layout: None) -> None: ...


def draw_canvas(canvas: _Canvas) -> None:
    """Draw through the narrow Agg canvas interface consumed by the exporter."""
    canvas.draw()


def set_manual_layout(fig: _LayoutFigure) -> None:
    """Freeze automatic layout before reserving the physical legend footer."""
    fig.set_layout_engine(None)


def _labeled_artists(axis: _KeyAxes) -> tuple[tuple[Artist, str], ...]:
    handles, labels = axis.get_legend_handles_labels()
    legend = axis.get_legend()
    if legend is not None:
        legend.remove()
    return tuple(zip(handles, labels, strict=True))


def _glyph(entry: KeyGlyph) -> Artist:
    match entry.kind:
        case "band":
            return Patch(facecolor=PALETTE[entry.role], alpha=0.15)
        case "text":
            return Line2D([], [], linestyle="None")
        case "line":
            line = Line2D(
                [], [], color=PALETTE[entry.role], marker=entry.marker, linestyle=entry.linestyle
            )
            if entry.outline:
                line.set_path_effects([effects.withStroke(linewidth=3, foreground=PALETTE["ink"])])
                line.set_markeredgecolor(PALETTE["ink"])
            return line
        case _:
            assert_never(entry.kind)


def interval_marker(status: Literal["estimated", "mechanism_exact", "unavailable_constant"]) -> str:
    """Distinguish stochastic estimates, proved values, and unavailable stochastic intervals."""
    match status:
        case "estimated":
            return "o"
        case "mechanism_exact":
            return "s"
        case "unavailable_constant":
            return "x"
        case _:
            assert_never(status)


def add_figure_key(fig: Figure, name: str, font_points: float) -> tuple[str, ...]:
    """Collect actual labeled marks, add declared meanings, and reserve a separate key area."""
    if name not in EXTRA_KEYS:
        message = f"Figure has no declared legend key: {name}"
        raise ContractError(message)
    entries = [pair for axis in fig.axes for pair in _labeled_artists(axis)]
    entries.extend((_glyph(entry), entry.label) for entry in EXTRA_KEYS[name])
    unique = {label: artist for artist, label in reversed(entries)}
    labels = tuple(dict.fromkeys(label for _, label in entries))
    if not labels:
        message = f"Figure legend key is empty: {name}"
        raise ContractError(message)
    draw_canvas(fig.canvas)
    set_manual_layout(fig)
    positions = [(axis, axis.get_position().bounds) for axis in fig.axes]
    anchored = [artist for artist in fig.findobj(Text) if artist.get_transform() is fig.transFigure]
    key = Legend(
        fig,
        [unique[label] for label in labels],
        [fill(label, width=32) for label in labels],
        loc="lower center",
        bbox_to_anchor=(0.5, 0),
        ncol=min(2, len(labels)),
        fontsize=font_points,
        title="Key",
        title_fontsize=font_points,
        borderaxespad=0,
        handlelength=1.8,
        columnspacing=1.3,
    )
    _ = fig.add_artist(key)
    key.set_gid("legend_figure_key")
    for index, text in enumerate(key.get_texts()):
        text.set_gid(f"key_label_{index}")
    draw_canvas(fig.canvas)
    bounds = key.get_window_extent()
    if bounds.width / fig.dpi > fig.get_figwidth() - 0.1:
        message = f"Figure legend exceeds available width: {name}"
        raise ContractError(message)
    previous_height = fig.get_figheight()
    footer = bounds.height / fig.dpi + 0.22
    height = previous_height + footer
    fig.set_size_inches(fig.get_figwidth(), height)
    for axis, (x, y, width, panel_height) in positions:
        axis.set_position(
            (x, (y * previous_height + footer) / height, width, panel_height * previous_height / height)
        )
    for text in anchored:
        x, y = text.get_position()
        text.set_position((x, (y * previous_height + footer) / height))
    key.set_bbox_to_anchor((0.5, 0.08 / height))
    draw_canvas(fig.canvas)
    return labels
