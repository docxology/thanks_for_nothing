# Copyright (c) 2026 Daniel Ari Friedman
"""Physical title wrapping and visible-text clearance for exported scientific figures."""

from textwrap import fill
from typing import Final

from matplotlib.figure import Figure
from matplotlib.text import Text

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.figure_keys import draw_canvas

_EXPORT_PIXEL_TOLERANCE: Final = 2.0


def wrap_titles(fig: Figure) -> None:
    """Fit panel titles to their rendered widths while retaining the publication font size."""
    draw_canvas(fig.canvas)
    for axis in fig.axes:
        label = axis.get_title(loc="left")
        if not label:
            continue
        title = next(t for t in axis.findobj(Text) if t.get_text() == label)
        available = axis.get_window_extent().width
        width = title.get_window_extent().width
        if width > available:
            characters = max(10, int(max(map(len, label.splitlines())) * available / width) - 1)
            title.set_text("\n".join(fill(line, characters) for line in label.splitlines()))
    draw_canvas(fig.canvas)


def require_text_clearance(fig: Figure) -> None:
    """Reject visible text cut by the physical export boundary rather than claiming legibility."""
    bounds = fig.get_window_extent()
    omitted: set[Text] = set()
    for axes in fig.axes:
        if not axes.get_visible():
            omitted.update(axes.findobj(Text))
            continue
        for axis in (axes.xaxis, axes.yaxis):
            visible = axes.axison and axis.get_visible()
            if not visible:
                omitted.update((axis.label, axis.get_offset_text()))
            low, high = sorted(axis.get_view_interval())
            for tick in (*axis.get_major_ticks(), *axis.get_minor_ticks()):
                if not visible or not low - 1e-9 <= tick.get_loc() <= high + 1e-9:
                    omitted.update((tick.label1, tick.label2))
    for text in fig.findobj(Text):
        if text in omitted or not text.get_visible() or not text.get_text():
            continue
        box = text.get_window_extent()
        if (
            box.x0 < -_EXPORT_PIXEL_TOLERANCE
            or box.y0 < -_EXPORT_PIXEL_TOLERANCE
            or box.x1 > bounds.x1 + _EXPORT_PIXEL_TOLERANCE
            or box.y1 > bounds.y1 + _EXPORT_PIXEL_TOLERANCE
        ):
            message = f"Figure text crosses export boundary: {text.get_text()!r}"
            raise ContractError(message)
