# Copyright (c) 2026 Daniel Ari Friedman
"""Symbolic settings and producer-bound readouts for distinct uses of nothing."""

from pathlib import Path
from textwrap import fill
from typing import Literal, assert_never

from matplotlib.patches import Circle, Ellipse, FancyArrowPatch

from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.concepts import CONCEPTS, NON_REIFICATION
from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, PlotAxes, figure, plot_grid, save


def _arrow(ax: PlotAxes, start: tuple[float, float], end: tuple[float, float]) -> None:
    _ = ax.add_patch(
        FancyArrowPatch(
            start, end, arrowstyle="->", mutation_scale=13, color=PALETTE["ink"], linewidth=1.3
        )
    )


def _node(ax: PlotAxes, x: float, y: float, text: str, role: str) -> None:
    _ = ax.add_patch(Circle((x, y), 0.07, facecolor="white", edgecolor=PALETTE[role], linewidth=1.5))
    _ = ax.text(x, y, text, ha="center", va="center", fontsize=12, color=PALETTE[role])


def _absence(ax: PlotAxes) -> None:
    role = CONCEPTS[0].role
    for x, text in ((0.13, "s"), (0.5, "0"), (0.87, "q")):
        _node(ax, x, 0.66, text, role)
    _arrow(ax, (0.22, 0.66), (0.40, 0.66))
    _arrow(ax, (0.59, 0.66), (0.77, 0.66))
    _ = ax.text(0.5, 0.46, r"$q(s\mid o=0)$", ha="center", fontsize=14)


def _missing(ax: PlotAxes) -> None:
    role = CONCEPTS[1].role
    _node(ax, 0.13, 0.66, "s", role)
    _node(ax, 0.87, 0.66, "q", role)
    _ = ax.plot([0.25, 0.75], [0.66] * 2, "--", color=PALETTE[role])
    _ = ax.text(0.5, 0.66, "?", ha="center", va="center", fontsize=20, color=PALETTE[role])
    _ = ax.text(0.5, 0.46, r"$q(s)=p(s)$", ha="center", fontsize=14)


def _value(ax: PlotAxes) -> None:
    role = CONCEPTS[2].role
    _ = ax.plot([0.14, 0.14, 0.86, 0.86], [0.60, 0.74, 0.74, 0.60], color=PALETTE[role])
    _ = ax.text(0.14, 0.54, "Reference", ha="center", fontsize=10.5)
    _ = ax.text(0.86, 0.54, "Actual", ha="center", fontsize=10.5)
    _ = ax.text(0.5, 0.76, r"$\Delta V$", ha="center", fontsize=14)
    _ = ax.text(0.5, 0.40, r"$V=r\,c-C_{\rm actual}$", ha="center", fontsize=15)


def _boundary(ax: PlotAxes, label: str = "Realizing Emptiness") -> None:
    role = NON_REIFICATION.role
    for offset, boundary_x in ((0.02, 0.13), (0.57, 0.22)):
        x = (offset + 0.05, offset + 0.17, offset + 0.32)
        _ = ax.plot(x, [0.61, 0.75, 0.61], "o-", color=PALETTE[role], markersize=4)
        _ = ax.plot([x[0], x[2]], [0.61] * 2, color=PALETTE[role])
        _ = ax.add_patch(
            Ellipse(
                (offset + boundary_x, 0.67),
                0.29,
                0.30,
                facecolor="none",
                edgecolor=PALETTE[role],
                linestyle="--",
                linewidth=1.4,
            )
        )
    _arrow(ax, (0.40, 0.67), (0.56, 0.67))
    _ = ax.text(0.5, 0.44, label, ha="center", fontsize=12, weight="bold")


def draw_concept_operation(ax: PlotAxes, code: Literal["A", "B", "C", "D"]) -> None:
    """Reuse the manuscript's defined symbolic operations without inventing new measurements."""
    _ = ax.set(xlim=(-0.02, 1.02), ylim=(0.32, 0.90))
    _ = ax.axis("off")
    match code:
        case "A":
            _absence(ax)
        case "B":
            _missing(ax)
        case "C":
            _value(ax)
        case "D":
            _boundary(ax, "Conditional use")
        case _:
            assert_never(code)


def concept_map(output: Path) -> FigureRecord:
    """Show the shared named concepts with separate symbolic operations and settings."""
    fig, _ = figure(6.54, 5.7, automatic_layout=False)
    fig.clear()
    fig.subplots_adjust(left=0.055, right=0.985, bottom=0.09, top=0.97, wspace=0.18, hspace=0.20)
    axes = plot_grid(fig, (2, 2))
    for ax, concept, draw in zip(axes, CONCEPTS, (_absence, _missing, _value, _boundary), strict=True):
        _ = ax.set(xlim=(-0.02, 1.02), ylim=(0, 1))
        _ = ax.axis("off")
        _ = ax.text(0, 0.98, concept.label, fontsize=11.5, weight="bold", va="top")
        _ = ax.plot([0, 1], [0.88] * 2, color=PALETTE[concept.role], linewidth=2)
        draw(ax)
        _ = ax.text(0.5, 0.31, fill(concept.meaning, 34), ha="center", va="top", fontsize=10.5)
        _ = ax.text(0.5, 0.14, fill(concept.operation, 35), ha="center", va="top", fontsize=10.5)
    _ = axes[-1].text(
        0.52,
        0.025,
        "Evidence, availability, value, and representation remain distinct.",
        ha="center",
        fontsize=10.5,
        weight="bold",
        transform=fig.transFigure,
    )
    return save(
        fig,
        output,
        "concept_map",
        "Four uses of nothing: separate questions and operations",
        "A observed absence, B missing observation, C counterfactual value, D non-reification.",
        ("data/concepts.json", "data/nothingness.json", "data/study.json"),
    )


def concept_operations(bundle: ResearchBundle, output: Path) -> FigureRecord:
    """Connect vocabulary to actual audit readouts and independent evaluation targets."""
    audit = bundle.nothingness
    base = {row.paired_id: row for row in bundle.study.rows if row.condition == Condition.NO_RECALL}
    shift = max(
        abs(row.post_world_well - base[row.paired_id].post_world_well)
        for row in bundle.study.rows
        if row.condition == Condition.ABSENCE
    )
    readouts = (
        (
            "Recorded no-event",
            f"P(low hazard)\n{audit.prior[0]:.3f} → {audit.observed_absence_posterior[0]:.3f}",
            f"Information update\n{audit.observed_absence_kl_bits:.3f} bits",
        ),
        (
            "Record unavailable",
            f"P(low hazard)\n{audit.prior[0]:.3f} → {audit.missing_posterior[0]:.3f}",
            f"Declared rule\n{audit.missing_kl_bits:.3f} bits",
        ),
        (
            "Specified alternative",
            f"Fixture value\n{audit.reference_value:g} cost units",
            f"Paired belief null\nmax |Δ belief| = {shift:g}",
        ),
        (
            "Examinable distinction",
            f"Costly inquiry\ncost = {bundle.practice.design.practice_cost:g}",
            "Retain or revise;\nassess new predictions",
        ),
    )
    fig, ax = figure(6.54, 5.5, automatic_layout=False)
    _ = ax.set(xlim=(0, 1), ylim=(0, 1))
    _ = ax.axis("off")
    for x, heading in ((0.16, "Input"), (0.52, "Model operation"), (0.85, "Readout / assessment")):
        _ = ax.text(x, 0.98, heading, ha="center", va="top", fontsize=11, weight="bold")
    for index, (concept, texts) in enumerate(zip(CONCEPTS, readouts, strict=True)):
        y = 0.87 - index * 0.22
        _ = ax.text(0.01, y, concept.label, fontsize=11, weight="bold", color=PALETTE[concept.role])
        _ = ax.plot([0.01, 0.99], [y - 0.025] * 2, color=PALETTE["grid"])
        for x, text in zip((0.16, 0.52, 0.85), texts, strict=True):
            _ = ax.text(x, y - 0.10, text, ha="center", va="center", fontsize=10.5)
        _arrow(ax, (0.32, y - 0.10), (0.36, y - 0.10))
        _arrow(ax, (0.68, y - 0.10), (0.72, y - 0.10))
    _ = ax.text(
        0.5,
        0.015,
        "A-C: finite audit readouts. D: an enabling mechanism; realization is unmeasured.",
        ha="center",
        fontsize=10.5,
    )
    return save(
        fig,
        output,
        "concept_operations",
        "From each concept to its implemented operation",
        "Producer-bound belief, information, valuation and inquiry readouts use separate units.",
        (
            "data/concepts.json",
            "data/nothingness.json",
            "data/study.json",
            "data/emptiness_practice.json",
        ),
    )
