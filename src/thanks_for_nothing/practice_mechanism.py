# Copyright (c) 2026 Daniel Ari Friedman
"""A declared computational dependency map, separated from the unmeasured human proposal."""

from pathlib import Path

from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from thanks_for_nothing.concepts import NON_REIFICATION
from thanks_for_nothing.practice_contracts import PracticeAudit
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, save


def practice_mechanism(audit: PracticeAudit, output: Path) -> FigureRecord:
    """Separate appreciation, cost, actual access, evidence selection and independent prediction."""
    fig, ax = figure(6.54, 6.4)
    _ = ax.set(xlim=(0, 1), ylim=(0, 1))
    _ = ax.axis("off")
    _ = ax.text(
        0.02,
        0.97,
        f"Concept {NON_REIFICATION.label} | Realizing Emptiness",
        fontsize=12,
        weight="bold",
        va="top",
    )
    _ = ax.text(
        0.02,
        0.91,
        "Appreciation-to-preference is unmeasured; the model declares it.",
        fontsize=10,
        va="top",
    )
    _ = ax.add_patch(
        FancyArrowPatch(
            (0.31, 0.88),
            (0.31, 0.83),
            arrowstyle="->",
            mutation_scale=12,
            linewidth=1.2,
            linestyle="--",
            color=PALETTE["no_recall"],
        )
    )
    stages = (
        (
            "1  Value examinability",
            f"Declared value = {audit.design.examinability_preference:g}",
            "No-preference control",
        ),
        (
            "2  Choose costly activity",
            f"Activity cost = {audit.design.practice_cost:g}",
            "Future patience / effort test",
        ),
        ("3  Gain effective access", "Expose an alternative repertoire", "Sham / blocked access"),
        ("4  Retain or revise", "Compare evidence; ties retain", "Useful-prior / tie controls"),
        ("5  Predict independently", "Freeze and assess on new outcomes", "Cost and risk stay separate"),
    )
    for index, (title, description, control) in enumerate(stages):
        y = 0.69 - 0.145 * index
        _ = ax.add_patch(
            FancyBboxPatch(
                (0.02, y),
                0.59,
                0.115,
                boxstyle="round,pad=0.01",
                facecolor="white",
                edgecolor=PALETTE["positive_recall"],
                linewidth=1.3,
            )
        )
        _ = ax.text(0.04, y + 0.084, title, fontsize=11, weight="bold", va="top")
        _ = ax.text(0.04, y + 0.039, description, fontsize=10, va="center")
        _ = ax.text(0.65, y + 0.055, control, fontsize=10, va="center")
        if index:
            _ = ax.add_patch(
                FancyArrowPatch(
                    (0.31, y + 0.145),
                    (0.31, y + 0.119),
                    arrowstyle="->",
                    mutation_scale=11,
                    linewidth=1.2,
                    color=PALETTE["ink"],
                )
            )
    _ = ax.text(
        0.02,
        0.035,
        "Continuing access permits future inquiry; no stage measures realization.",
        fontsize=10,
        va="center",
    )
    return save(
        fig,
        output,
        "practice_mechanism",
        "Appreciation and the enacted inquiry mechanism",
        "A dashed unmeasured human link leads to five declared finite-model stages and their controls.",
        ("data/concepts.json", "data/emptiness_practice.json", "data/upstream_practice.json"),
    )
