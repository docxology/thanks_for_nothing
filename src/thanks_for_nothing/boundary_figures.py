# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound figures for contingency questions, the reference intervention and sample convergence."""

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.ticker import MaxNLocator, NullFormatter

from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.boundary_design import contingency_channel
from thanks_for_nothing.boundary_structure_figure import boundary_structure
from thanks_for_nothing.figure_keys import interval_marker
from thanks_for_nothing.intervals import quantile_pair
from thanks_for_nothing.visual_style import (
    PALETTE,
    PROBABILITY_CMAP,
    PROBABILITY_TEXT_THRESHOLD,
    FigureRecord,
    figure,
    panels,
    plot_grid,
    save,
    shared_color_scale,
)
from thanks_for_nothing.visual_tokens import BOUNDARY_LABELS, BOUNDARY_MARKERS, BOUNDARY_ROLES

if TYPE_CHECKING:
    from matplotlib.image import AxesImage

__all__ = [
    "boundary_allocation",
    "boundary_convergence",
    "boundary_information",
    "boundary_outcomes",
    "boundary_structure",
]


def boundary_information(audit: BoundaryGazeAudit, output: Path) -> FigureRecord:
    """Show conditional rather than marginal information, with the full label-equivalence null."""
    fig, _ = figure(6.54, 5.8)
    fig.clear()
    axes = plot_grid(fig, (2, 3))
    reliability = audit.design.probe_reliabilities[len(audit.design.probe_reliabilities) // 2]
    encodings = len(audit.design.scene_maps)
    diagnostic = contingency_channel(reliability).reshape(3, 3, 3) * 3
    images: list[AxesImage] = []
    for index, axis in enumerate(axes):
        h = index % 3
        matrix = (
            diagnostic[:, :, h : h + 1].reshape(3, 3) if index < encodings else np.full((3, 3), 1 / 3)
        )
        images.append(axis.imshow(matrix, cmap=PROBABILITY_CMAP, vmin=0, vmax=1))
        for a in range(3):
            for r in range(3):
                value = float(np.sum(matrix[a : a + 1, r : r + 1]))
                _ = axis.text(
                    r,
                    a,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    color=PALETTE["artwork_overlay"]
                    if value < PROBABILITY_TEXT_THRESHOLD
                    else PALETTE["ink"],
                )
        _ = axis.set_xticks([0, 1, 2], ["0", "1", "2"])
        _ = axis.set_yticks([0, 1, 2], ["0", "1", "2"])
        _ = axis.set(
            xlabel="Response r",
            ylabel="Randomized action a",
            title=f"{'Diagnostic' if index < encodings else 'Label-only'} H{h}",
        )
    shared_color_scale(fig, images[0], "P(response | randomized action, encoding)")
    return save(
        fig,
        output,
        "boundary_information",
        "A boundary question needs an informative relation",
        (
            "Conditional response probabilities for the middle-cost query; all action and "
            "response marginals are uniform."
        ),
        ("data/boundary_gaze.json",),
    )


def boundary_outcomes(audit: BoundaryGazeAudit, output: Path) -> FigureRecord:
    """Plot diagnostic visual-reference contrasts from the 84-member family, retaining exact nulls."""
    fig, _ = figure(6.54, 7.0)
    fig.clear()
    axes = plot_grid(fig, (3, 2))
    indexed = {row.key: row for row in audit.region.intervals}
    conditions = tuple(c for c in audit.design.conditions if c != "visual")
    for index, axis in enumerate(axes):
        h = index // 2
        endpoint = audit.design.endpoints[index % 2]
        _ = axis.axvline(0, color=PALETTE["ink"], lw=1)
        for y, condition in enumerate(conditions):
            row = indexed[f"diagnostic/H{h}/{condition}/visual/{endpoint}"]
            color = PALETTE[BOUNDARY_ROLES[condition]]
            if row.low is None or row.high is None:
                _ = axis.plot([row.mean], [y], "x", color=color)
            else:
                _ = axis.errorbar(
                    [row.mean],
                    [y],
                    xerr=[[row.mean - row.low], [row.high - row.mean]],
                    fmt=interval_marker(row.status),
                    capsize=3,
                    color=color,
                )
        _ = axis.set_yticks(
            list(range(len(conditions))),
            [BOUNDARY_LABELS[c] for c in conditions] if index % 2 == 0 else [""] * len(conditions),
        )
        endpoint_label = "anchor risk (nats)" if index % 2 == 0 else "boundary Brier"
        _ = axis.set(
            ylim=(len(conditions) - 0.5, -0.6),
            xlabel="Difference from visual only",
            title=f"{'ABCDEF'[index]}  H{h}: {endpoint_label}",
        )
        axis.xaxis.set_major_locator(MaxNLocator(nbins=3))
    return save(
        fig,
        output,
        "boundary_gaze_outcomes",
        "Scene and boundary inquiry at a common reference target",
        (
            "Diagnostic-regime contrasts with global 84-member empirical-bootstrap bounds; exact "
            "constants are squares, unavailable constants crosses."
        ),
        ("data/boundary_gaze.json",),
    )


def boundary_allocation(audit: BoundaryGazeAudit, output: Path) -> FigureRecord:
    """Separate question allocation, current-scene prediction and expenditure; means are descriptive."""
    fig, _ = figure(6.54, 7.4)
    fig.clear()
    axes = plot_grid(fig, (3, 1))
    for index, (axis, metric, title, unit) in enumerate(
        zip(
            axes,
            ("boundary_query_fraction", "mean_scene_regret", "mean_cost"),
            (
                "A  Where the sampling budget goes",
                "B  Prediction in the current scene",
                "C  Expenditure is an additional outcome",
            ),
            ("Boundary-query fraction", "Excess loss (nats / outcome)", "Declared cost / decision"),
            strict=True,
        )
    ):
        for offset, regime, role in (
            (-0.1, "diagnostic", "positive_recall"),
            (0.1, "label_only", "absence_appreciation"),
        ):
            groups = [
                np.asarray(
                    [
                        getattr(row, metric)
                        for row in audit.episodes
                        if row.regime == regime and row.condition == condition
                    ],
                    dtype=np.float64,
                )
                for condition in audit.design.conditions
            ]
            means = [float(np.mean(group, dtype=np.float64)) for group in groups]
            for position, group in enumerate(groups):
                low, high = quantile_pair(group, (0.25, 0.75))
                _ = axis.plot([position + offset] * 2, [low, high], color=PALETTE[role], linewidth=2)
            _ = axis.plot(
                [x + offset for x in range(len(means))],
                means,
                "o" if regime == "diagnostic" else "s",
                color=PALETTE[role],
                label=regime.replace("_", " ").capitalize(),
            )
        _ = axis.set_xticks(
            list(range(len(audit.design.conditions))),
            [BOUNDARY_LABELS[c].replace(" ", "\n") for c in audit.design.conditions],
        )
        _ = axis.set(ylabel=unit, title=title, ylim=(-0.04, 1.15) if index == 0 else (0, None))
        if index == 0:
            _ = axis.legend(loc="upper right", ncol=1)
    return save(
        fig,
        output,
        "boundary_gaze_allocation",
        "Inquiry has a sampling and cost tradeoff",
        (
            "Descriptive means over the declared equal fixed-stratum mixture; repeated decisions "
            "are not independent samples."
        ),
        ("data/boundary_gaze.json",),
    )


def boundary_convergence(audit: BoundaryGazeAudit, output: Path) -> FigureRecord:
    """Display fixed nested prefixes, without implying that every estimate must move monotonically."""
    fig, _ = figure(6.54, 6.0)
    fig.clear()
    top, bottom = panels(fig, vertical=True)
    excluded_boundary = len(audit.design.scene_maps) - 1
    for condition in audit.design.conditions:
        if condition == "visual":
            continue
        rows = [
            r
            for r in audit.convergence
            if r.regime == "diagnostic"
            and r.boundary == excluded_boundary
            and r.condition == condition
            and r.reference == "visual"
            and r.endpoint == "anchored_regret"
        ]
        x = [float(r.replicates_per_stratum) for r in rows]
        color = PALETTE[BOUNDARY_ROLES[condition]]
        marker = BOUNDARY_MARKERS[condition]
        _ = top.plot(
            x, [r.mean for r in rows], marker + "-", color=color, label=BOUNDARY_LABELS[condition]
        )
        _ = bottom.plot(x, [r.standard_error for r in rows], marker + "-", color=color)
    _ = top.axhline(0, color=PALETTE["ink"], lw=1)
    _ = top.set(ylabel="Anchored contrast (nats)", title="A  H2: fixed-prefix point estimates")
    _ = top.legend(loc="center right", ncol=3)
    _ = bottom.set(
        ylabel="Monte Carlo standard error", title="B  Precision of the paired mean", ylim=(0, None)
    )
    for axis in (top, bottom):
        _ = axis.set(xscale="log")
        axis.xaxis.set_minor_formatter(NullFormatter())
        _ = axis.set_xticks(list(audit.design.prefixes), [str(n) for n in audit.design.prefixes])
        _ = axis.set(xlabel="Independent paired replicates per fixed scene stratum")
    return save(
        fig,
        output,
        "boundary_gaze_convergence",
        "Larger independent samples and Monte Carlo convergence",
        (
            "Predeclared nested prefixes at H2; standard errors describe simulation sampling, "
            "not human populations or bootstrap quantile error."
        ),
        ("data/boundary_gaze.json",),
    )
