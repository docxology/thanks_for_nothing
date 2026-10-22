# Copyright (c) 2026 Daniel Ari Friedman
"""Ensemble trajectories and paired changes from complete agent-level daily records."""

from pathlib import Path

import numpy as np

from thanks_for_nothing.contracts import Condition, StudyResult
from thanks_for_nothing.intervals import quantile_pair
from thanks_for_nothing.visual_style import LABELS, PALETTE, FigureRecord, figure, plot_grid, save
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE


def trajectories(study: StudyResult, output: Path) -> FigureRecord:
    """Separate between-agent variability from paired changes; bands are IQRs, not CIs."""
    fig, _ = figure(6.54, 6.0)
    fig.clear()
    axes = plot_grid(fig, (2, 2))
    days = list(range(1, study.design.baseline_days + study.design.intervention_days + 1))
    indexed = {(r.luckiness, r.condition, r.replicate, r.day): r.world_well for r in study.traces}
    for column, world in enumerate((min(study.design.luckiness), max(study.design.luckiness))):
        top, bottom = axes[column], axes[column + 2]
        baseline = np.asarray(
            [
                [indexed[world, Condition.NO_RECALL, replicate, day] for day in days]
                for replicate in range(study.design.replicates)
            ],
            dtype=np.float64,
        )
        for condition, marker in (
            (Condition.NO_RECALL, "o-"),
            (Condition.POSITIVE, "s-"),
            (Condition.RANDOM, "^--"),
        ):
            values = np.asarray(
                [
                    [indexed[world, condition, replicate, day] for day in days]
                    for replicate in range(study.design.replicates)
                ],
                dtype=np.float64,
            )
            quartiles = [
                quantile_pair(values[:, i : i + 1].reshape(-1), (0.25, 0.75)) for i in range(len(days))
            ]
            lows, highs = [q[0] for q in quartiles], [q[1] for q in quartiles]
            _ = top.fill_between(days, lows, highs, color=PALETTE[condition], alpha=0.10)
            _ = top.plot(
                days,
                [float(np.mean(values[:, i : i + 1], dtype=np.float64)) for i in range(len(days))],
                marker,
                color=PALETTE[condition],
                label=LABELS[condition],
            )
            if condition != Condition.NO_RECALL:
                changes = DISPLAY_SCALE * (values - baseline)
                quartiles = [
                    quantile_pair(changes[:, i : i + 1].reshape(-1), (0.25, 0.75))
                    for i in range(len(days))
                ]
                low, high = [q[0] for q in quartiles], [q[1] for q in quartiles]
                _ = bottom.fill_between(days, low, high, color=PALETTE[condition], alpha=0.12)
                _ = bottom.plot(
                    days,
                    [float(np.mean(changes[:, i : i + 1], dtype=np.float64)) for i in range(len(days))],
                    marker,
                    color=PALETTE[condition],
                    label=f"{LABELS[condition]} minus no recall",
                )
        _ = top.set(
            ylim=(0, 1),
            ylabel="Daily mean P(well)",
            title=f"{'AB'[column]}  World p={world:g}",
        )
        _ = bottom.axhline(0, color=PALETTE["ink"], lw=1)
        _ = bottom.set(
            xlabel="Day",
            ylabel=f"Paired ΔP(well) x {DISPLAY_SCALE:g}",
            title=f"{'CD'[column]}  Paired change",
        )
        for axis in (top, bottom):
            _ = axis.axvline(study.design.baseline_days + 0.5, color=PALETTE["grid"], lw=2)
            _ = axis.set_xticks(
                [days[0], study.design.baseline_days, days[-1]],
                [str(days[0]), str(study.design.baseline_days), str(days[-1])],
            )
        _ = top.legend(loc="upper center")
        _ = bottom.legend(loc="upper center")
    return save(
        fig,
        output,
        "learning_trajectories",
        "Ensemble learning and paired daily changes",
        "Means and between-agent IQRs retain all independent units; paired panels expose overlap.",
        ("data/study.json",),
    )
