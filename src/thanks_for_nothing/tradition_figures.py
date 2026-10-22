# Copyright (c) 2026 Daniel Ari Friedman
"""Readable, source-bound textual comparison with no numerical score for a tradition."""

from pathlib import Path
from typing import Final, Protocol

from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from matplotlib.textpath import TextPath
from matplotlib.transforms import Bbox

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.traditions import TraditionsRecord
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, save

_MAX_BODY_HEIGHT_PT: Final = 620


class _ExtentPath(Protocol):
    def get_extents(self) -> Bbox: ...


def _path_width(path: _ExtentPath) -> float:
    return path.get_extents().width


def _text_width(text: str, font: FontProperties) -> float:
    return _path_width(TextPath((0, 0), text, prop=font))


def _wrap(text: str, width: float, *, bold: bool = False) -> str:
    font = FontProperties(family="DejaVu Sans", size=10.5, weight="bold" if bold else "normal")
    lines: list[str] = []
    current = ""
    for word in text.split():
        if _text_width(word, font) > width:
            message = f"Tradition figure has an unbreakable label: {word}"
            raise ContractError(message)
        proposed = f"{current} {word}".strip()
        if _text_width(proposed, font) <= width:
            current = proposed
        elif current:
            lines.append(current)
            current = word
    return "\n".join((*lines, current))


def world_traditions(output: Path) -> FigureRecord:
    """Compare textual witnesses along shared questions without asserting shared doctrines."""
    record = TraditionsRecord.model_validate_json(
        (output.parent / "data/world_traditions.json").read_text()
    )
    columns = (10.0, 132.0, 295.0)
    right = 460.0
    wrapped = tuple(
        (
            _wrap(row.tradition, columns[1] - columns[0] - 12, bold=True),
            _wrap(row.witness, columns[1] - columns[0] - 12),
            _wrap(row.absence, columns[2] - columns[1] - 12),
            _wrap(row.response, right - columns[2]),
        )
        for row in record.selection.rows
    )
    heights = tuple(
        max(row[0].count("\n") + row[1].count("\n") + 2, *(text.count("\n") + 1 for text in row[2:]))
        * 12.6
        + 13
        for row in wrapped
    )
    height = sum(heights) + 83
    if height > _MAX_BODY_HEIGHT_PT:
        message = "Tradition figure exceeds a readable manuscript page; shorten display labels"
        raise ContractError(message)
    fig, ax = figure(6.54, height / 72, automatic_layout=False)
    fig.set_size_inches(6.54, height / 72)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    _ = ax.set(xlim=(0, 6.54 * 72), ylim=(0, height))
    _ = ax.axis("off")
    _ = ax.text(
        10,
        height - 9,
        "Thanks for Nothing: distinct textual representations",
        fontsize=12,
        weight="bold",
        va="top",
    )
    headers = ("Textual witness", "Absence / relinquishment", "Appreciation / response")
    for x, header in zip(columns, headers, strict=True):
        _ = ax.text(x, height - 34, header, fontsize=10.5, weight="bold", color=PALETTE["ink"])
    y = height - 47
    sources = {source.key: source for source in record.sources}
    for index, (row, texts, row_height) in enumerate(
        zip(record.selection.rows, wrapped, heights, strict=True)
    ):
        if index % 2 == 0:
            _ = ax.add_patch(
                Rectangle(
                    (columns[0] - 4, y + 3 - row_height),
                    right - columns[0] + 8,
                    row_height,
                    facecolor=PALETTE["grid"],
                    edgecolor="none",
                    alpha=0.35,
                )
            )
        _ = ax.plot([columns[0], right], [y + 3] * 2, color=PALETTE["grid"], linewidth=0.7)
        witness_y = y - 3 - (texts[0].count("\n") + 1) * 12.6
        entries = (
            (columns[0], y - 3, texts[0], "bold", "ink"),
            (columns[0], witness_y, texts[1], "normal", "no_recall"),
            (columns[1], y - 3, texts[2], "normal", "ink"),
            (columns[2], y - 3, texts[3], "normal", "ink"),
        )
        for x, text_y, text, weight, role in entries:
            artist = ax.text(
                x,
                text_y,
                text,
                fontsize=10.5,
                va="top",
                linespacing=1.2,
                weight=weight,
                color=PALETTE[role],
            )
            if x == columns[0]:
                artist.set_url(str(sources[row.source_keys[0]].url))
        y -= row_height
    _ = ax.text(
        10,
        12,
        "Selected witnesses; interpretive summaries, no shared measured construct.",
        fontsize=10.5,
    )
    return save(
        fig,
        output,
        "world_traditions",
        "Distinct textual representations of Thanks for Nothing",
        record.selection.scope,
        ("data/world_traditions.json",),
    )
