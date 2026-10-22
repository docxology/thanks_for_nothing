# Copyright (c) 2026 Daniel Ari Friedman
"""Paired gaze consequences with explicit endpoint units and replicate-level uncertainty."""

from pathlib import Path

import numpy as np

from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.visual_style import LABELS, PALETTE, FigureRecord, figure, plot_grid, save
from thanks_for_nothing.visual_tokens import GAZE_LABELS, GAZE_ROLES


def gaze_transfer_summary(audit: GazeAudit, output: Path) -> FigureRecord:
    """Separate descriptive stratum means from pooled paired confidence intervals."""
    fig, _ = figure(6.54, 7.4)
    fig.clear()
    top, middle, bottom = plot_grid(fig, (3, 1))
    strata = sorted({row.luckiness for row in audit.transfer})
    all_means: list[float] = []
    for condition, marker, label in (
        ("no_recall", "o-", "None"),
        ("positive_recall", "s--", "Positive"),
        ("matched_random_recall", "^:", "Random"),
    ):
        means = [
            100
            * float(
                np.mean(
                    [
                        row.positive_policy_change
                        for row in audit.transfer
                        if row.condition == condition
                        and row.luckiness == stratum
                        and row.bridge == "likelihood"
                    ]
                )
            )
            for stratum in strata
        ]
        all_means.extend(means)
        _ = top.plot(strata, means, marker, color=PALETTE[condition], label=label)
    padding = max(0.1, (max(all_means) - min(all_means)) / 4)
    _ = top.set(
        xlabel="Luckiness stratum",
        ylabel="Change (pp)",
        ylim=(min(all_means) - padding, max(all_means) + 4 * padding),
        title="A  Pre/post positive-location policy mass",
    )
    _ = top.legend(loc="upper center", ncol=3)
    for axis, endpoint, scale, title, units in (
        (
            middle,
            "positive_policy_change",
            100,
            "B  Paired policy contrasts",
            "Percentage points minus no recall",
        ),
        (
            bottom,
            "balanced_loss_change",
            1,
            "C  Paired scene-prediction contrasts",
            "Nats / outcome minus no recall",
        ),
    ):
        rows = [
            row
            for row in audit.contrasts
            if row.experiment == "transfer"
            and row.endpoint == endpoint
            and row.context == "likelihood"
            and row.reference == "no_recall"
        ]
        _ = axis.axvline(0, color=PALETTE["no_recall"], lw=1)
        for index, row in enumerate(rows):
            interval = row.intervals
            _ = axis.errorbar(
                [scale * interval.mean],
                [index],
                xerr=[
                    [scale * max(0, interval.mean - interval.analytic_low)],
                    [scale * max(0, interval.analytic_high - interval.mean)],
                ],
                fmt="o",
                capsize=3,
                color=PALETTE[row.condition],
            )
        _ = axis.set_yticks(list(range(len(rows))), [LABELS[row.condition] for row in rows])
        _ = axis.set(ylim=(len(rows) - 0.4, -0.5), xlabel=units, title=title)
    return save(
        fig,
        output,
        "gaze_transfer_summary",
        "Learned attention shifts and predictive consequences",
        "Stratum means and paired intervals separate positivity from balanced scene-prediction loss.",
        ("data/gaze.json", "data/study.json"),
    )


def gaze_inquiry_summary(audit: GazeAudit, output: Path) -> FigureRecord:
    """Keep scene prediction and the movement penalty separate, including exact sham nulls."""
    fig, _ = figure(6.54, 7.4)
    fig.clear()
    axes = plot_grid(fig, (2, 1))
    for axis, endpoint, title, units in zip(
        axes,
        ("mean_balanced_log_loss", "mean_movement_cost"),
        ("A  Scene-wide predictive consequence", "B  Movement penalty"),
        ("Nats / outcome minus restricted utility", "Penalty / step minus restricted utility"),
        strict=True,
    ):
        rows = [
            row
            for row in audit.contrasts
            if row.experiment == "active"
            and row.endpoint == endpoint
            and row.reference == "pragmatic_restricted"
        ]
        _ = axis.axvline(0, color=PALETTE["no_recall"], lw=1)
        for index, row in enumerate(rows):
            interval = row.intervals
            _ = axis.errorbar(
                [interval.mean],
                [index],
                xerr=[
                    [max(0, interval.mean - interval.analytic_low)],
                    [max(0, interval.analytic_high - interval.mean)],
                ],
                fmt="o" if row.context == "stationary" else "s",
                capsize=3,
                color=PALETTE[GAZE_ROLES[row.condition]],
            )
        _ = axis.set_yticks(
            list(range(len(rows))),
            [f"{row.context.capitalize()}: {GAZE_LABELS[row.condition]}" for row in rows],
        )
        _ = axis.set(ylim=(len(rows) - 0.4, -0.6), xlabel=units, title=title)
    return save(
        fig,
        output,
        "gaze_inquiry_summary",
        "Representation access and active sampling have distinct consequences",
        "Paired intervals retain stationary/reversal contexts and movement costs.",
        ("data/gaze.json",),
    )
