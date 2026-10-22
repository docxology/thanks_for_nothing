# Copyright (c) 2026 Daniel Ari Friedman
"""Numerical manuscript tables bound to admitted research records."""

from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.calibration import CalibrationAudit
from thanks_for_nothing.calibration_fixtures import LABELS, Fixture
from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE


def _interval(low: float | None, high: float | None) -> str:
    if low is None or high is None:
        return "Unavailable"
    return f"[{DISPLAY_SCALE * low:.3f}, {DISPLAY_SCALE * high:.3f}]"


def _contrast(first: str, second: str) -> str:
    labels = {
        "no_recall": "None",
        "positive_recall": "Positive",
        "matched_random_recall": "Random",
        "absence_appreciation": "Absence",
    }
    return f"{labels[first]} - {labels[second]}"


def main_findings(bundle: ResearchBundle) -> str:
    """Keep primary effects, pointwise intervals and Monte Carlo decisions distinct."""
    level = 100 * bundle.statistics.contrasts[0].estimate.confidence
    lines: list[str] = []
    for endpoint, heading in (
        ("optimism_change", "Optimism-task change"),
        ("brier_change", "Brier-loss change"),
    ):
        lines.extend(
            (
                f"**{heading}.** Estimates and interval bounds are multiplied by {DISPLAY_SCALE:g}.",
                "",
                f"| Contrast | Mean | Bootstrap t {level:g}% interval | Holm p; MC decision |",
                "| --- | ---: | --- | --- |",
            )
        )
        for row in bundle.statistics.contrasts:
            if row.endpoint != endpoint:
                continue
            estimate = row.estimate
            name = _contrast(row.first, row.second)
            lines.append(
                "".join(
                    (
                        f"| {name} | {DISPLAY_SCALE * estimate.mean_difference:.3f} | ",
                        f"{_interval(estimate.studentized.low, estimate.studentized.high)} | ",
                        f"{row.holm_p_value:.5f}; {row.decision} |",
                    )
                )
            )
        lines.append("")
    return "\n".join(lines)


def interval_findings(bundle: ResearchBundle) -> str:
    """Compare all three interval procedures on the same primary paired contrasts."""
    level = 100 * bundle.statistics.contrasts[0].estimate.confidence
    lines: list[str] = []
    for endpoint, heading in (
        ("optimism_change", "Optimism-task change"),
        ("brier_change", "Brier-loss change"),
    ):
        lines.extend(
            (
                f"**{heading}; all values x{DISPLAY_SCALE:g}.**",
                "",
                f"| Contrast | Percentile {level:g}% | Bootstrap t {level:g}% | Analytic t {level:g}% |",
                "| --- | --- | --- | --- |",
            )
        )
        for row in bundle.statistics.contrasts:
            if row.endpoint != endpoint:
                continue
            e = row.estimate
            name = _contrast(row.first, row.second)
            lines.append(
                "".join(
                    (
                        f"| {name} | {_interval(e.ci95_low, e.ci95_high)} | ",
                        f"{_interval(e.studentized.low, e.studentized.high)} | ",
                        f"{_interval(e.analytic_t_ci95_low, e.analytic_t_ci95_high)} |",
                    )
                )
            )
        lines.append("")
    return "\n".join(lines)


def calibration_findings(audit: CalibrationAudit) -> str:
    """Keep the total replication denominator even when a method returns no interval."""
    level = 100 * (1 - audit.alpha)
    lines = [
        f"Each fixture used {audit.rows[0].experiments} independent experiments, with",
        f"{audit.rows[0].sample_size} paired units per stratum, {audit.bootstrap_draws} bootstrap",
        f"draws and {audit.permutation_draws} sign-flip draws. Methods share each generated sample.",
        "",
        "| Fixture | Percentile cover | Analytic t cover | Bootstrap t cover | t available |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in audit.rows:
        n = row.experiments
        name = LABELS[Fixture(row.fixture)]
        lines.append(
            "".join(
                (
                    f"| {name} | {row.covered}/{n} | {row.analytic_t_covered}/{n} | ",
                    f"{row.studentized_covered}/{n} | {row.studentized_available}/{n} |",
                )
            )
        )
    lines.extend(
        (
            "",
            "Coverage counts use the total denominator: unavailable bootstrap t intervals count as",
            "noncoverage. Availability is shown separately, without dropping degenerate samples.",
            "Exact binomial intervals and Monte Carlo standard errors accompany rates in the data.",
            "",
            f"| Mean-zero fixture | Rejections | Exact binomial {level:g}% interval | Sign symmetry |",
            "| --- | ---: | --- | --- |",
        )
    )
    for row in audit.rows:
        if row.true_difference != 0:
            continue
        name = LABELS[Fixture(row.fixture)]
        symmetry = "Violated" if "violated" in row.sign_flip_assumption else "Satisfied"
        lines.append(
            "".join(
                (
                    f"| {name} | {row.rejections}/{row.experiments} | ",
                    f"[{row.rejection_ci_low:.3f}, {row.rejection_ci_high:.3f}] | {symmetry} |",
                )
            )
        )
    positive = next(row for row in audit.rows if row.true_difference != 0)
    discrete = next(row for row in audit.rows if row.fixture == Fixture.DISCRETE)
    conditional = (
        f"{100 * discrete.studentized_covered / discrete.studentized_available:.2f}%"
        if discrete.studentized_available
        else "unavailable"
    )
    lines.extend(
        (
            "",
            "For the rare Bernoulli fixture, exact bootstrap t availability under the declared",
            f"failure rule is {100 * audit.discrete_availability.exact_availability:.2f}%; observed",
            f"availability is {100 * discrete.studentized_available / discrete.experiments:.2f}%.",
            f"Unconditional coverage is {100 * discrete.studentized_coverage_rate:.2f}%, whereas",
            f"coverage conditional on an available interval is {conditional}. The exact calculation",
            "benchmarks availability alone; it does not establish a coverage guarantee.",
            "",
            f"The +1 SD Gaussian control rejected in {positive.rejections}/{positive.experiments}",
            f"experiments ({level:g}% binomial interval [{positive.rejection_ci_low:.3f},",
            f"{positive.rejection_ci_high:.3f}]). Skewed mean-zero fixtures deliberately violate",
            "the sign-flip assumption; any rejection distortion remains a reported boundary.",
            "No seed, benchmark or method is selected to achieve a desired coverage rate.",
        )
    )
    return "\n".join(lines)


def heterogeneity_findings(report: StatisticalReport) -> str:
    """Report exploratory world dependence without claiming transport to human populations."""
    lines: list[str] = []
    for endpoint, label in (
        ("brier_change", "Brier-loss change"),
        ("nll_change", "observation log-loss change"),
    ):
        row = next(
            r
            for r in report.heterogeneity.weighting
            if r.endpoint == endpoint and r.second == Condition.NO_RECALL
        )
        strata = [
            r
            for r in report.heterogeneity.strata
            if r.endpoint == endpoint and r.second == Condition.NO_RECALL
        ]
        negative = sum(r.intervals.mean < 0 for r in strata)
        positive = sum(r.intervals.mean > 0 for r in strata)
        leave_out = (
            f"[{row.leave_one_out_min:.6f}, {row.leave_one_out_max:.6f}]"
            if row.leave_one_out_min is not None and row.leave_one_out_max is not None
            else "undefined for a single world"
        )
        lines.append(
            " ".join(
                (
                    f"For positive minus no recall, {label} had an equal-grid mean of",
                    f"{row.equal_grid.mean:.6f}; {negative} world strata had negative means and",
                    f"{positive} had positive means. Holding stratum estimates fixed, arbitrary",
                    f"nonnegative world weights yielded [{row.convex_min:.6f}, {row.convex_max:.6f}].",
                    f"The leave-one-world-out range was {leave_out}.",
                )
            )
        )
    return "\n\n".join(lines)
