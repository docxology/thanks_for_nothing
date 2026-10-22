# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound joint uncertainty and family-coverage figures at manuscript width."""

from pathlib import Path

from matplotlib.ticker import MaxNLocator, StrMethodFormatter

from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_joint import GazeUncertainty
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, panels, plot_grid, save

_NAMES = {
    "positive_recall": "Positive",
    "matched_random_recall": "Random",
    "absence_appreciation": "Absence",
    "no_recall": "None",
    "pragmatic_restricted": "restricted utility",
    "pragmatic_open": "open utility",
    "uniform_open": "uniform",
    "inquiry_open": "Inquiry",
}
_FIXTURES = {
    "independent_gaussian": "Independent Gaussian",
    "correlated_gaussian": "Correlated Gaussian",
    "heterogeneous_gaussian": "Three variance strata",
    "centered_exponential": "Centered exponential",
    "rare_bernoulli": "Rare Bernoulli (.01)",
}


def joint_gaze_summary(gaze: GazeAudit, audit: GazeUncertainty, output: Path) -> FigureRecord:
    """Compare pointwise and simultaneous bounds without changing effect units or hiding nulls."""
    fig, _ = figure(6.54, 7.4)
    fig.clear()
    axes = plot_grid(fig, (3, 1))
    joint = {row.key: row for row in audit.region.intervals}
    for axis, experiment, bridge, title in zip(
        axes,
        ("transfer", "transfer", "active"),
        ("likelihood", "posterior_readout", ""),
        (
            "A  Likelihood transfer: scene risk",
            "B  Readout projection: scene risk",
            "C  Inquiry beyond open access",
        ),
        strict=True,
    ):
        rows = [
            row
            for row in gaze.contrasts
            if (
                experiment == "transfer"
                and row.experiment == experiment
                and row.endpoint == "balanced_loss_change"
                and row.context == bridge
            )
            or (
                experiment == "active"
                and row.experiment == experiment
                and row.endpoint == "mean_balanced_log_loss"
                and row.condition == "inquiry_open"
                and row.reference in ("pragmatic_open", "uniform_open")
            )
        ]
        labels: list[str] = []
        _ = axis.axvline(0, color=PALETTE["ink"], lw=1)
        for index, row in enumerate(rows):
            prefix = "" if experiment == "transfer" else f"{row.context.capitalize()}: "
            labels.append(f"{prefix}{_NAMES[row.condition]} - {_NAMES[row.reference]}")
            point = row.intervals
            region = joint[
                f"{row.experiment}/{row.context}/{row.condition}/{row.reference}/{row.endpoint}"
            ]
            _ = axis.errorbar(
                [point.mean],
                [index - 0.12],
                xerr=[[point.mean - point.analytic_low], [point.analytic_high - point.mean]],
                fmt="o",
                capsize=2,
                color=PALETTE["no_recall"],
                label="Pointwise analytic t" if index == 0 else "_nolegend_",
            )
            if region.low is not None and region.high is not None:
                _ = axis.errorbar(
                    [region.mean],
                    [index + 0.12],
                    xerr=[[region.mean - region.low], [region.high - region.mean]],
                    fmt="D" if region.status == "estimated" else "s",
                    capsize=3,
                    color=PALETTE["positive_recall"]
                    if region.status == "estimated"
                    else PALETTE["absence_appreciation"],
                    label="Joint bootstrap" if index == 0 else "_nolegend_",
                )
            else:
                _ = axis.plot([region.mean], [index + 0.12], "x", color=PALETTE["harm"])
                labels[-1] += " (unavailable)"
        _ = axis.set_yticks(list(range(len(rows))), labels)
        axis.xaxis.set_major_locator(MaxNLocator(nbins=3))
        axis.xaxis.set_major_formatter(StrMethodFormatter("{x:.3g}"))
        _ = axis.set(
            ylim=(len(rows) - 0.5, -1.8),
            xlabel="Nats / outcome; negative favors first condition",
            title=title,
        )
        _ = axis.legend(loc="upper center", ncol=2)
    return save(
        fig,
        output,
        "gaze_joint_uncertainty",
        "Joint uncertainty across the exploratory gaze family",
        "Pointwise analytic and joint bootstrap intervals; squares retain exact valuation identities.",
        ("data/gaze.json", "data/gaze_uncertainty.json"),
    )


def joint_coverage(audit: GazeUncertainty, output: Path) -> FigureRecord:
    """Keep joint coverage, unadjusted family coverage and availability on independent panels."""
    fig, _ = figure(6.54, 6.6)
    fig.clear()
    top, bottom = panels(fig, vertical=True)
    labels = [_FIXTURES[row.fixture] for row in audit.calibration]
    _ = top.axvline(100 * audit.design.confidence, color=PALETTE["ink"], lw=1)
    for index, row in enumerate(audit.calibration):
        for offset, rate, marker, role, name in (
            (-0.12, row.pointwise_family_coverage, "o", "no_recall", "Pointwise t, all targets"),
            (0.12, row.joint_coverage, "D", "positive_recall", "Joint bootstrap, all targets"),
        ):
            _ = top.errorbar(
                [100 * rate.rate],
                [index + offset],
                xerr=[[100 * (rate.rate - rate.low)], [100 * (rate.high - rate.rate)]],
                fmt=marker,
                capsize=3,
                color=PALETTE[role],
                label=name if index == 0 else "_nolegend_",
            )
        rate = row.family_availability
        _ = bottom.errorbar(
            [100 * rate.rate],
            [index],
            xerr=[[100 * (rate.rate - rate.low)], [100 * (rate.high - rate.rate)]],
            fmt="s",
            capsize=3,
            color=PALETTE["absence_appreciation"],
        )
    for axis in (top, bottom):
        _ = axis.set_yticks(list(range(len(labels))), labels)
        _ = axis.set(xlim=(-2, 104), ylim=(len(labels) - 0.5, -1.7))
    _ = top.set(xlabel="Joint coverage of all zero means (%)", title="A  Known-answer family coverage")
    _ = top.legend(loc="upper center")
    _ = bottom.set(
        xlabel="Complete stochastic region available (%)",
        title="B  Availability; not conditional coverage",
    )
    return save(
        fig,
        output,
        "joint_coverage",
        "Family coverage and availability under distribution stress",
        "Independent experiment rates with exact binomial bounds retain skew and rare-event failures.",
        ("data/gaze_uncertainty.json",),
    )
