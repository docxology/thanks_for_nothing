# Copyright (c) 2026 Daniel Ari Friedman
"""Publication-scale views of paired learning, loss and semantic controls."""

from pathlib import Path
from statistics import quantiles

import numpy as np
from matplotlib.ticker import MaxNLocator

from thanks_for_nothing.concepts import COUNTERFACTUAL_VALUE
from thanks_for_nothing.contracts import Condition, StudyResult
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.visual_style import LABELS, PALETTE, FigureRecord, figure, panels, save
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE


def calibration_by_world(study: StudyResult, report: StatisticalReport, output: Path) -> FigureRecord:
    """Distinguish between-unit spread from uncertainty in a paired contrast."""
    fig, _ = figure(6.54, 6.0)
    fig.clear()
    top, bottom = panels(fig, vertical=True)
    lower: list[float] = []
    upper: list[float] = []
    for condition, marker in zip(
        (Condition.NO_RECALL, Condition.POSITIVE, Condition.RANDOM), ("o-", "s-", "^-"), strict=True
    ):
        groups = [
            [r.brier_post for r in study.rows if r.condition == condition and r.luckiness == luck]
            for luck in study.design.luckiness
        ]
        quartiles = [quantiles(values, n=4, method="inclusive") for values in groups]
        lows, highs = [q[0] for q in quartiles], [q[2] for q in quartiles]
        lower.extend(lows)
        upper.extend(highs)
        _ = top.plot(
            study.design.luckiness,
            [float(np.mean(v)) for v in groups],
            marker,
            color=PALETTE[condition],
            label=LABELS[condition],
        )
        _ = top.fill_between(study.design.luckiness, lows, highs, color=PALETTE[condition], alpha=0.09)
    span = max(max(upper) - min(lower), 1e-6)
    _ = top.set(
        ylim=(min(lower) - 0.15 * span, max(upper) + 0.15 * span),
        ylabel="Held-out binary Brier loss",
        title=f"A  Means and unit IQRs (n={study.design.replicates}/world)",
    )
    _ = top.legend(loc="upper center", ncol=3)
    delta_low: list[float] = []
    delta_high: list[float] = []
    for second, marker in ((Condition.NO_RECALL, "o-"), (Condition.RANDOM, "s--")):
        rows = [
            r for r in report.heterogeneity.strata if r.endpoint == "brier_change" and r.second == second
        ]
        means = [DISPLAY_SCALE * r.intervals.mean for r in rows]
        lows = [DISPLAY_SCALE * (r.intervals.mean - r.intervals.analytic_low) for r in rows]
        highs = [DISPLAY_SCALE * (r.intervals.analytic_high - r.intervals.mean) for r in rows]
        delta_low.extend(m - lo for m, lo in zip(means, lows, strict=True))
        delta_high.extend(m + hi for m, hi in zip(means, highs, strict=True))
        _ = bottom.errorbar(
            [r.world for r in rows],
            means,
            yerr=[lows, highs],
            fmt=marker,
            capsize=3,
            color=PALETTE[second],
            label=f"Positive minus {LABELS[second].lower()}",
        )
    _ = bottom.axhline(0, color=PALETTE["ink"], lw=1)
    floor, ceiling = min(0, *delta_low), max(0, *delta_high)
    span = max(ceiling - floor, 1e-6)
    _ = bottom.set(
        ylim=(floor - 0.12 * span, ceiling + 0.12 * span),
        xlabel="World probability of well state (fixed stratum)",
        ylabel=f"Paired Brier change x {DISPLAY_SCALE:g}",
        title="B  Pointwise analytic t intervals",
    )
    _ = bottom.legend(loc="upper center")
    for ax in (top, bottom):
        _ = ax.set_xticks(study.design.luckiness, [f"{p:g}" for p in study.design.luckiness])
    return save(
        fig,
        output,
        "calibration_by_world",
        "Predictive loss and paired world contrasts",
        "Brier means and unit IQRs; paired analytic t intervals are exploratory. Lower is better.",
        ("data/study.json", "data/statistics.json"),
    )


def paired_contrasts(report: StatisticalReport, output: Path) -> FigureRecord:
    """Compare percentile and studentized intervals for the unchanged primary estimands."""
    fig, _ = figure(6.54, 6.2)
    fig.clear()
    axes = panels(fig, vertical=True)
    short = {
        "no_recall": "No recall",
        "positive_recall": "Positive",
        "matched_random_recall": "Random",
        "absence_appreciation": "Absence value",
    }
    for ax, endpoint, title in zip(
        axes,
        ("optimism_change", "brier_change"),
        ("A  Optimism-task change", "B  Binary Brier change (lower is better)"),
        strict=True,
    ):
        rows = [r for r in report.contrasts if r.endpoint == endpoint]
        for index, row in enumerate(rows):
            estimate = row.estimate
            mean = DISPLAY_SCALE * estimate.mean_difference
            _ = ax.plot(
                [DISPLAY_SCALE * estimate.ci95_low, DISPLAY_SCALE * estimate.ci95_high],
                [index - 0.09, index - 0.09],
                color=PALETTE[row.first],
            )
            _ = ax.plot(
                [mean],
                [index - 0.09],
                "o",
                color=PALETTE[row.first],
                label="Percentile interval" if index == 0 else "_nolegend_",
            )
            interval = estimate.studentized
            if interval.low is not None and interval.high is not None:
                _ = ax.plot(
                    [DISPLAY_SCALE * interval.low, DISPLAY_SCALE * interval.high],
                    [index + 0.09, index + 0.09],
                    color=PALETTE["ink"],
                )
                _ = ax.plot(
                    [mean],
                    [index + 0.09],
                    "D",
                    color=PALETTE["ink"],
                    label="Bootstrap t interval" if index == 0 else "_nolegend_",
                )
        _ = ax.plot([0, 0], [-0.35, len(rows) - 0.5], color=PALETTE["ink"])
        _ = ax.set_yticks(range(len(rows)), [f"{short[r.first]}\n- {short[r.second]}" for r in rows])
        _ = ax.set(
            ylim=(-0.9, len(rows) - 0.5),
            title=title,
            xlabel=f"Paired change contrast x {DISPLAY_SCALE:g}",
        )
        ax.invert_yaxis()
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
        _ = ax.legend(loc="upper center", ncol=2)
    return save(
        fig,
        output,
        "paired_contrasts",
        "Primary paired estimates with two interval methods",
        "Primary paired percentile and bootstrap t intervals; exact nulls lack studentization.",
        ("data/statistics.json",),
    )


def appreciation_null(study: StudyResult, output: Path) -> FigureRecord:
    """Show reference-dependent value beside exact paired inference invariants."""
    fig, _ = figure(6.54, 3.6)
    fig.clear()
    left, right = panels(fig)
    absent = [r for r in study.rows if r.condition == Condition.ABSENCE]
    base = {(r.luckiness, r.replicate): r for r in study.rows if r.condition == Condition.NO_RECALL}
    groups = [[r.appreciation for r in absent if r.luckiness == luck] for luck in study.design.luckiness]
    quartiles = [quantiles(values, n=4, method="inclusive") for values in groups]
    _ = left.plot(
        study.design.luckiness,
        [float(np.mean(v)) for v in groups],
        "o-",
        color=PALETTE[Condition.ABSENCE],
    )
    _ = left.fill_between(
        study.design.luckiness,
        [q[0] for q in quartiles],
        [q[2] for q in quartiles],
        color=PALETTE[Condition.ABSENCE],
        alpha=0.12,
    )
    _ = left.set(
        xlabel="World P(well)",
        ylabel="Counterfactual value",
        ylim=(0, None),
        title=COUNTERFACTUAL_VALUE.label,
    )
    _ = right.axis("off")
    _ = right.set(title="Inference controls")
    maxima = (
        (
            "Belief",
            max(abs(r.post_world_well - base[r.luckiness, r.replicate].post_world_well) for r in absent),
        ),
        (
            "Brier loss",
            max(abs(r.brier_post - base[r.luckiness, r.replicate].brier_post) for r in absent),
        ),
        ("Log loss", max(abs(r.nll_post - base[r.luckiness, r.replicate].nll_post) for r in absent)),
    )
    for index, (name, value) in enumerate(maxima):
        _ = right.text(0.02, 0.72 - index * 0.2, f"Max |Δ {name}| = {value:.1g}", fontsize=11)
    _ = right.text(0.02, 0.05, f"{len(absent)} paired units\nExact by the valuation rule", fontsize=10)
    return save(
        fig,
        output,
        "appreciation_null",
        "Value with unchanged inference",
        "Counterfactual value varies; belief, Brier and log-loss differences are zero by design.",
        ("data/concepts.json", "data/study.json"),
    )
