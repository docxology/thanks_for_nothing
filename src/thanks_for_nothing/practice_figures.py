# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound figures separating chosen inquiry, effective access and held-out prediction."""

from pathlib import Path

import numpy as np
from matplotlib.ticker import LogFormatter, MaxNLocator

from thanks_for_nothing.practice_contracts import ExactDecisionAudit, PracticeAudit
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, panels, plot_grid, save
from thanks_for_nothing.visual_tokens import PRACTICE_LABELS as NAMES
from thanks_for_nothing.visual_tokens import PRACTICE_ROLES as ROLES
from thanks_for_nothing.visual_tokens import PROCESS_ROLES


def practice_policies(audit: PracticeAudit, output: Path) -> FigureRecord:
    """Show the gap between activity and access in each declared context."""
    fig, _ = figure(6.54, 5.8)
    fig.clear()
    axes = panels(fig, vertical=True)
    label_inside_above = 0.9
    for index, (axis, context) in enumerate(zip(axes, audit.design.contexts, strict=True)):
        rows = [row for row in audit.contrasts if row.context == context.name]
        x = np.arange(len(rows), dtype=np.float64)
        _ = axis.bar(
            x - 0.17,
            [r.mean_practice_rate for r in rows],
            width=0.32,
            color=PALETTE["no_recall"],
            label="Chosen activity",
        )
        _ = axis.bar(
            x + 0.17,
            [r.mean_access_rate for r in rows],
            width=0.32,
            color=PALETTE["positive_recall"],
            hatch="///",
            edgecolor=PALETTE["ink"],
            linewidth=0.7,
            label="Effective access",
        )
        for position, row in zip(x, rows, strict=True):
            for offset, rate in (
                (-0.17, row.mean_practice_rate),
                (0.17, row.mean_access_rate),
            ):
                _ = axis.text(
                    float(position + offset),
                    min(0.98, rate + 0.025),
                    f"{rate:.2g}",
                    ha="center",
                    va="top" if rate > label_inside_above else "bottom",
                    color=PALETTE["artwork_overlay"] if rate > label_inside_above else PALETTE["ink"],
                )
        _ = axis.set_xticks(x, [NAMES[r.condition] for r in rows])
        _ = axis.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0", "0.25", "0.5", "0.75", "1"])
        _ = axis.set(
            ylim=(0, 1),
            ylabel="Fraction of windows",
            title=f"{'AB'[index]}  {context.name.capitalize()} context",
        )
        _ = axis.legend(loc="upper center", ncol=2)
    return save(
        fig,
        output,
        "practice_policies",
        "Valuing inquiry is distinct from gaining access",
        "Chosen activity and effective access differ in sham and no-access controls.",
        ("data/emptiness_practice.json", "data/upstream_practice.json"),
    )


def practice_revision(audit: PracticeAudit, output: Path) -> FigureRecord:
    """Retain trajectory means and paired replicate-level uncertainty as different summaries."""
    fig, _ = figure(6.54, 7.2)
    fig.clear()
    top, bottom = panels(fig, vertical=True)
    context = next(c for c in audit.design.contexts if c.name == "reversal")
    windows = list(range(1, len(context.probabilities) + 1))
    _ = top.plot(windows, context.probabilities, ":", color=PALETTE["ink"], label="Process")
    for condition, marker in (("rigid", "s-"), ("inquiry", "o-"), ("no_preference", "^--")):
        means = [
            float(
                np.mean(
                    [
                        r.forecast
                        for r in audit.rows
                        if r.context == context.name
                        and r.condition == condition
                        and r.window == window - 1
                    ]
                )
            )
            for window in windows
        ]
        _ = top.plot(windows, means, marker, color=PALETTE[ROLES[condition]], label=NAMES[condition])
    _ = top.set(
        ylim=(0, 1),
        xlabel="Calibration / assessment window",
        ylabel="P(channel 0)",
        title="A  Forecasts under reversal",
    )
    _ = top.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0", "0.25", "0.5", "0.75", "1"])
    _ = top.legend(loc="upper center", ncol=2)
    _ = bottom.axvline(0, color=PALETTE["no_recall"], lw=1)
    for index, row in enumerate(audit.contrasts):
        interval = row.heldout_loss_difference
        _ = bottom.errorbar(
            [interval.mean],
            [index],
            xerr=[
                [max(0.0, interval.mean - interval.analytic_low)],
                [max(0.0, interval.analytic_high - interval.mean)],
            ],
            fmt="o" if row.context == "stationary" else "s",
            capsize=3,
            color=PALETTE[ROLES[row.condition]],
        )
    _ = bottom.set_yticks(
        list(range(len(audit.contrasts))),
        [f"{r.context.capitalize()}: {NAMES[r.condition]}" for r in audit.contrasts],
    )
    _ = bottom.set(
        ylim=(len(audit.contrasts) - 0.4, -0.7),
        xlabel="Loss minus rigid (nats / observation)",
        title="B  Paired held-out contrasts",
    )
    return save(
        fig,
        output,
        "practice_revision",
        "Revisability under stationary and changing conditions",
        "Reversal forecasts and paired intervals; sham and no-access forecasts retain exact nulls.",
        ("data/emptiness_practice.json",),
    )


def exact_decision(audit: ExactDecisionAudit, output: Path) -> FigureRecord:
    """Show every possible calibration count and its declared process probability."""
    fig, _ = figure(6.54, 6.4)
    fig.clear()
    top, middle, bottom = plot_grid(fig, (3, 1))
    counts = [row.zero_count for row in audit.rows]
    for axis in (top, middle, bottom):
        axis.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
        _ = axis.set(xlim=(min(counts) - 0.5, max(counts) + 0.5))
    _ = top.axhline(0, color=PALETTE["no_recall"], lw=1)
    _ = top.plot(counts, [r.log_bayes_factor for r in audit.rows], color=PALETTE["ink"])
    for supports, marker, role, label in (
        (True, "o", "positive_recall", "Select open family"),
        (False, "s", "matched_random_recall", "Retain restriction"),
    ):
        chosen = [row for row in audit.rows if row.supports_open == supports]
        _ = top.plot(
            [r.zero_count for r in chosen],
            [r.log_bayes_factor for r in chosen],
            marker,
            color=PALETTE[role],
            label=label,
        )
    _ = top.set(ylabel="Log BF (open / restricted)", title="A  Exhaustive decision region")
    _ = top.legend(loc="upper right")
    for axis in (middle, bottom):
        for left, right in zip(audit.rows, audit.rows[1:], strict=False):
            if left.supports_open != right.supports_open:
                _ = axis.axvline(
                    (left.zero_count + right.zero_count) / 2,
                    color=PALETTE["ink"],
                    linestyle=":",
                    lw=1,
                    label="Decision boundary between counts",
                )
        for index, point in enumerate(audit.operating_points):
            _ = axis.plot(
                counts,
                point.count_probabilities,
                ("o-", "s--", "^:", "D-.")[index % 4],
                color=PALETTE[PROCESS_ROLES[index % len(PROCESS_ROLES)]],
                label=f"Process p = {point.process_probability:g}",
            )
    _ = middle.set(
        ylim=(0, None),
        ylabel="Probability mass",
        title="B  Count probabilities: linear scale",
    )
    _ = bottom.set(
        xlabel=f"Channel-0 count in {audit.calibration_samples} calibration observations",
        ylabel="Probability mass (log scale)",
        yscale="log",
        title="C  Same probabilities: rare tails remain visible",
    )
    bottom.yaxis.set_major_formatter(LogFormatter())
    bottom.yaxis.set_minor_formatter(LogFormatter())
    _ = bottom.legend(loc="upper center")
    return save(
        fig,
        output,
        "exact_decision",
        "Exact count decisions and conditional selection probabilities",
        "Linear and log count masses show rare tails; dotted boundaries separate family decisions.",
        ("data/exact_decision.json",),
    )
