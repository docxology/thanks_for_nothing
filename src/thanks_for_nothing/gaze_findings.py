# Copyright (c) 2026 Daniel Ari Friedman
"""Manuscript tables drawn from every declared gaze contrast, including exact nulls."""

from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_joint import GazeUncertainty
from thanks_for_nothing.intervals import MeanIntervals
from thanks_for_nothing.visual_tokens import GAZE_LABELS

_CONDITION_LABELS = {
    **GAZE_LABELS,
    "no_recall": "None",
    "positive_recall": "Positive",
    "matched_random_recall": "Random",
    "absence_appreciation": "Absence",
}
_ENDPOINT_LABELS = {
    "positive_policy_change": "Positive probability change",
    "balanced_loss_change": "Scene-risk change",
    "mean_balanced_log_loss": "Scene risk",
    "positive_occupancy": "Positive occupancy",
    "mean_movement_cost": "Movement penalty",
}


def _bounds(low: float | None, high: float | None) -> str:
    if low is None or high is None:
        return "Unavailable"
    return f"[{low:+.6f}, {high:+.6f}]"


def _summary(interval: MeanIntervals) -> str:
    return f"{interval.mean:+.6f} {_bounds(interval.studentized.low, interval.studentized.high)}"


def gaze_source_findings(audit: GazeAudit) -> str:
    """Print exact source occupancy in its positive/negative/neutral plotting order."""
    lines = [
        "| Source profile | Positive (%) | Negative (%) | Neutral (%) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, values in (
        ("Positive template", audit.source.positive_percent),
        ("Negative template", audit.source.negative_percent),
    ):
        lines.append(f"| {name} | " + " | ".join(f"{value:.2f}" for value in values) + " |")
    return "\n".join(lines)


def gaze_main_findings(audit: GazeAudit) -> str:
    """Keep direct parameter transfer, readout projection and structural access distinct."""
    index = {
        (r.experiment, r.context, r.condition, r.reference, r.endpoint): r.intervals
        for r in audit.contrasts
    }
    direct = index["transfer", "likelihood", "positive_recall", "no_recall", "positive_policy_change"]
    risk = index["transfer", "likelihood", "positive_recall", "no_recall", "balanced_loss_change"]
    readout = index[
        "transfer", "posterior_readout", "positive_recall", "no_recall", "positive_policy_change"
    ]
    stationary = index[
        "active", "stationary", "inquiry_open", "pragmatic_restricted", "mean_balanced_log_loss"
    ]
    reversal = index[
        "active", "reversal", "inquiry_open", "pragmatic_restricted", "mean_balanced_log_loss"
    ]
    return " ".join(
        (
            "Direct likelihood transfer gave a positive-recall-minus-no-recall change in",
            f"positive-location probability of {_summary(direct)}; multiplying by 100 gives",
            f"{100 * direct.mean:.3f} percentage points. The corresponding scene-risk change was",
            f"{_summary(risk)} nats per outcome, indicating worse prediction under this bridge.",
            f"The readout bridge instead gave {_summary(readout)} probability units.",
            "All brackets are pointwise bootstrap t intervals, not multiplicity-adjusted tests.",
            "Open inquiry minus restricted utility changed scene-wide prequential log loss by",
            f"{_summary(stationary)} in the stationary context and {_summary(reversal)} in the",
            "reversal context. Access to the omitted candidate explains the reversal advantage:",
            "open utility and uniform open sampling also improve over the restricted reference.",
            "The full table retains the direct inquiry-versus-open-utility and",
            "inquiry-versus-uniform comparisons; their risk intervals include zero.",
        )
    )


def gaze_interval_findings(audit: GazeAudit) -> str:
    """Expose all exploratory estimates and availability across three interval methods."""
    level = 100 * audit.contrasts[0].intervals.confidence
    lines: list[str] = []
    for experiment, context in dict.fromkeys((r.experiment, r.context) for r in audit.contrasts):
        lines.extend(
            (
                f"**{experiment.capitalize()}: {context.replace('_', ' ')}.**",
                "",
                " ".join(
                    (
                        f"| Contrast; endpoint | Mean | Percentile {level:g}% |",
                        f"Bootstrap t {level:g}% | Analytic t {level:g}% |",
                    )
                ),
                "| --- | ---: | --- | --- | --- |",
            )
        )
        for row in audit.contrasts:
            if (row.experiment, row.context) != (experiment, context):
                continue
            e = row.intervals
            label = f"{_CONDITION_LABELS[row.condition]} - {_CONDITION_LABELS[row.reference]}; "
            label += _ENDPOINT_LABELS[row.endpoint]
            lines.append(
                "".join(
                    (
                        f"| {label} | {e.mean:+.6f} | {_bounds(e.percentile_low, e.percentile_high)} | ",
                        f"{_bounds(e.studentized.low, e.studentized.high)} | ",
                        f"{_bounds(e.analytic_low, e.analytic_high)} |",
                    )
                )
            )
        lines.append("")
    lines.extend(
        (
            "Exact constant contrasts have zero-width percentile and analytic intervals; the",
            "bootstrap t method reports degenerate_sample rather than manufacturing an interval.",
            "Probability endpoints are in probability units; loss uses natural-log nats per",
            "outcome; movement is the GNN-weighted unit-square distance per sampled step.",
        )
    )
    return "\n".join(lines)


def gaze_joint_findings(audit: GazeUncertainty) -> str:
    """State the covered family, exact identities, Monte Carlo precision and unavailable subset."""
    region = audit.region
    counts = {
        status: sum(row.status == status for row in region.intervals)
        for status in ("estimated", "mechanism_exact", "unavailable_constant")
    }
    critical = "unavailable" if region.critical_value is None else f"{region.critical_value:.4f}"
    mc_low = "-infinity" if region.critical_mc_low is None else f"{region.critical_mc_low:.6f}"
    mc_high = "+infinity" if region.critical_mc_high is None else f"{region.critical_mc_high:.6f}"
    bracket = f"[{mc_low}, {mc_high}]" if region.critical_value is not None else "not estimated"
    return " ".join(
        (
            f"The exploratory joint region has status **{region.status}** across",
            f"{len(region.intervals)}",
            f"contrasts: {counts['estimated']} estimated, {counts['mechanism_exact']} mechanism-exact",
            f"zeros and {counts['unavailable_constant']} unavailable sample constants.",
            f"Its original-SE-standardized maximum uses {region.draws:,} joint draws and critical",
            f"value {critical}. The separate {100 * region.monte_carlo_confidence:g}% Monte Carlo",
            f"bracket for that conditional critical quantile is {bracket}.",
            "This is nominal joint uncertainty under bootstrap approximation, not measured coverage",
            "for the gaze experiment or a new confirmatory testing family. Mechanism identities",
            "supply their own zero contrasts; an accidentally constant sample would remain unavailable.",
        )
    )


def joint_calibration_findings(audit: GazeUncertainty) -> str:
    """Report all-experiment family coverage; retain skew and unavailable rare-event outcomes."""
    rate_level = 100 * audit.calibration[0].joint_coverage.confidence
    lines = [
        f"Each fixture uses {audit.design.calibration_experiments} independent experiments,",
        (
            f"{audit.design.calibration_units} units per stratum, "
            f"{audit.calibration[0].contrasts} zero-mean contrasts and"
        ),
        f"{audit.design.calibration_draws:,} joint bootstrap draws per experiment.",
        "Coverage requires every target and interval; unavailable cases count as noncoverage.",
        f"Both coverage columns give percentages and exact binomial {rate_level:g}% intervals.",
        "",
        "| Fixture | Joint region (%) | Pointwise t, complete family (%) | Available (%) |",
        "| --- | --- | --- | ---: |",
    ]
    for row in audit.calibration:
        joint = row.joint_coverage
        point = row.pointwise_family_coverage
        lines.append(
            "".join(
                (
                    f"| {row.fixture.replace('_', ' ')} | {100 * joint.rate:.1f} ",
                    f"[{100 * joint.low:.1f}, {100 * joint.high:.1f}] | {100 * point.rate:.1f} ",
                    f"[{100 * point.low:.1f}, {100 * point.high:.1f}] | ",
                    f"{100 * row.family_availability.rate:.1f} |",
                )
            )
        )
    scope = "These are operating characteristics of the stated fixtures, not human power or universal"
    lines.append(
        f"{scope} coverage. Rare-event sample constants are not licensed as exact population zeros."
    )
    return "\n".join(lines)


def gaze_joint_interval_findings(gaze: GazeAudit, audit: GazeUncertainty) -> str:
    """Keep every original contrast alongside its joint bound and exact/unavailable status."""
    index = {row.key: row for row in audit.region.intervals}
    lines: list[str] = []
    for experiment, context in dict.fromkeys((r.experiment, r.context) for r in gaze.contrasts):
        lines.extend(
            (
                f"**{experiment.capitalize()}: {context.replace('_', ' ')}.**",
                "",
                f"| Contrast; endpoint | Joint {100 * audit.region.confidence:g}% bounds | Status |",
                "| --- | --- | --- |",
            )
        )
        for row in gaze.contrasts:
            if (row.experiment, row.context) != (experiment, context):
                continue
            interval = index[f"{experiment}/{context}/{row.condition}/{row.reference}/{row.endpoint}"]
            label = f"{_CONDITION_LABELS[row.condition]} - {_CONDITION_LABELS[row.reference]}; "
            label += _ENDPOINT_LABELS[row.endpoint]
            lines.append(
                "".join(
                    (
                        f"| {label} | {_bounds(interval.low, interval.high)} | ",
                        f"{interval.status.replace('_', ' ')} |",
                    )
                )
            )
        lines.append("")
    return "\n".join(lines)
