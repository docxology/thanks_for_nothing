# Copyright (c) 2026 Daniel Ari Friedman
"""Shared diagram primitives for source-bound cognitive task views."""

from dataclasses import dataclass
from typing import Literal, assert_never

from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

from thanks_for_nothing.visual_style import PALETTE, PlotAxes, figure


@dataclass(frozen=True, slots=True)
class SituationNode:
    """A world, evidence, or model variable at a schematic position."""

    center: tuple[float, float]
    text: str
    role: str = "no_recall"
    shape: Literal["world", "record", "belief"] = "record"


@dataclass(frozen=True, slots=True)
class SituationLink:
    """A declared computational dependency; dashed links identify alternative mappings."""

    start: tuple[float, float]
    end: tuple[float, float]
    dashed: bool = False


def situation_canvas(
    title: str, question: str, *, stacked: bool = False
) -> tuple[Figure, PlotAxes, PlotAxes, PlotAxes]:
    """Place one cognitive setting above two quantitative result panels."""
    fig, _ = figure(6.54, 6.9 if stacked else 6.3, automatic_layout=not stacked)
    fig.clear()
    if stacked:
        context = GridSpec(1, 1, figure=fig, left=0.035, right=0.965, bottom=0.61, top=0.96)
        readouts = GridSpec(
            2,
            1,
            figure=fig,
            left=0.29,
            right=0.965,
            bottom=0.075,
            top=0.54,
            hspace=0.85,
            height_ratios=(0.75, 1.15),
        )
        setting: PlotAxes = fig.add_subplot(context[0, 0])
        left: PlotAxes = fig.add_subplot(readouts[0, 0])
        right: PlotAxes = fig.add_subplot(readouts[1, 0])
    else:
        grid = GridSpec(2, 2, figure=fig, height_ratios=(1.15, 1.1))
        setting = fig.add_subplot(grid[0, :])
        left = fig.add_subplot(grid[1, 0])
        right = fig.add_subplot(grid[1, 1])
    _ = setting.set(xlim=(-0.02, 1.02), ylim=(-0.08, 1.30), title=f"a  {title}")
    diagram_note(setting, (0.5, 1.20), question)
    _ = setting.axis("off")
    return fig, setting, left, right


def draw_node(axis: PlotAxes, node: SituationNode) -> None:
    """Draw a task variable in normalized schematic coordinates."""
    x, y = node.center
    color = PALETTE[node.role]
    match node.shape:
        case "world":
            _ = axis.add_patch(
                Ellipse((x, y), 0.18, 0.30, facecolor="white", edgecolor=color, linewidth=1.5)
            )
        case "record":
            _ = axis.add_patch(
                FancyBboxPatch(
                    (x - 0.09, y - 0.10),
                    0.18,
                    0.20,
                    boxstyle="square,pad=0.01",
                    facecolor="white",
                    edgecolor=color,
                    linewidth=1.5,
                )
            )
        case "belief":
            _ = axis.add_patch(
                FancyBboxPatch(
                    (x - 0.10, y - 0.11),
                    0.20,
                    0.22,
                    boxstyle="round,pad=0.01",
                    facecolor="white",
                    edgecolor=color,
                    linewidth=1.7,
                )
            )
        case _:
            assert_never(node.shape)
    _ = axis.text(x, y, node.text, ha="center", va="center", color=color, fontsize=10.5)


def draw_link(axis: PlotAxes, link: SituationLink) -> None:
    """Draw an explicitly declared dependency between task variables."""
    _ = axis.add_patch(
        FancyArrowPatch(
            link.start,
            link.end,
            arrowstyle="->",
            mutation_scale=12,
            color=PALETTE["ink"],
            linewidth=1.3,
            linestyle="--" if link.dashed else "-",
        )
    )


def diagram_note(axis: PlotAxes, position: tuple[float, float], text: str) -> None:
    """Label a setting with the same physical typography as its quantitative panels."""
    _ = axis.text(*position, text, ha="center", va="center", fontsize=10.5, linespacing=1.35)
