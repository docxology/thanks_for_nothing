# Copyright (c) 2026 Daniel Ari Friedman
"""Admission of actual figure bytes, visible keys, colors, sources, and placement fonts."""

import re
from pathlib import Path
from typing import Final
from xml.etree import ElementTree as ET

import matplotlib as mpl
from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring
from matplotlib.colors import to_hex
from pydantic import TypeAdapter

from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.visual_style import (
    DIVERGING_CMAP,
    MIN_FONT_POINTS,
    PROBABILITY_CMAP,
    FigureRecord,
)
from thanks_for_nothing.visual_tokens import PALETTE, REQUIRED_FIGURES

_SVG_NAMESPACE: Final = {"s": "http://www.w3.org/2000/svg"}
_SVG_WIDTH_TOLERANCE: Final = 1e-6
_SVG_FONT_TOLERANCE: Final = 1e-5
_ALLOWED_COLORS: Final = frozenset(color.lower() for color in PALETTE.values()) | frozenset(
    to_hex(mpl.colormaps[name](i / 255))
    for name in (DIVERGING_CMAP, PROBABILITY_CMAP)
    for i in range(256)
)


def _fonts_valid(svg: str, row: FigureRecord) -> bool:
    fonts = tuple(float(match.group(1)) for match in re.finditer(r"font-size:\s*([0-9.]+)px", svg))
    width = re.search(r'<svg[^>]*\bwidth="([0-9.]+)pt"', svg)
    if not fonts or width is None or row.width_inches <= 0:
        return False
    actual_width = float(width.group(1)) / 72
    publication = min(fonts) * min(1.0, 6.54 / actual_width)
    return (
        abs(actual_width - row.width_inches) < _SVG_WIDTH_TOLERANCE
        and abs(min(fonts) - row.min_font_points) < _SVG_FONT_TOLERANCE
        and abs(publication - row.publication_min_font_points) < _SVG_FONT_TOLERANCE
        and publication >= MIN_FONT_POINTS - 1e-6
    )


def legend_valid(svg: str, labels: tuple[str, ...]) -> bool:
    """Require each declared legend entry to exist as readable vector text in the actual key."""
    if not labels or len(labels) != len(set(labels)):
        return False
    try:
        root = fromstring(svg)
    except (ET.ParseError, DefusedXmlException):
        return False
    key = root.find(".//s:g[@id='legend_figure_key']", _SVG_NAMESPACE)
    if key is None:
        return False
    entries = {g.get("id", ""): g for g in key.iter() if g.get("id", "").startswith("key_label_")}
    if len(entries) != len(labels):
        return False
    for index, label in enumerate(labels):
        node = entries.get(f"key_label_{index}")
        if node is None or " ".join(" ".join(node.itertext()).split()) != " ".join(label.split()):
            return False
    return True


def palette_valid(svg: str) -> bool:
    """Admit the shared categorical palette and the two declared quantitative color scales."""
    colors = {
        match.group(1).lower()
        for match in re.finditer(r'(?:fill|stroke)(?:\s*:\s*|=")(#[\da-fA-F]{6})', svg)
    }
    return bool(colors) and colors <= _ALLOWED_COLORS


def figures_valid(output: Path) -> bool:
    """Check the full source-bound inventory and the rendered visual contract."""
    figures = TypeAdapter(tuple[FigureRecord, ...]).validate_json(
        (output / "reports/figure_source_map.json").read_text()
    )
    names = {row.name for row in figures}
    if names != set(REQUIRED_FIGURES) or len(names) != len(figures):
        return False
    for row in figures:
        png, vector = output / f"figures/{row.name}.png", output / f"figures/{row.name}.svg"
        paths = (png, vector, *(output / source for source in row.source_artifacts))
        if any(not p.is_file() or not p.resolve().is_relative_to(output.resolve()) for p in paths):
            return False
        svg = vector.read_text()
        if (
            not row.alt
            or row.min_font_points < MIN_FONT_POINTS
            or len(row.source_artifacts) != len(row.source_sha256)
            or not _fonts_valid(svg, row)
            or not legend_valid(svg, row.legend_labels)
            or not palette_valid(svg)
            or file_digest(png) != row.png_sha256
            or file_digest(vector) != row.svg_sha256
        ):
            return False
        if any(
            file_digest(output / s) != digest
            for s, digest in zip(row.source_artifacts, row.source_sha256, strict=True)
        ):
            return False
    return True
