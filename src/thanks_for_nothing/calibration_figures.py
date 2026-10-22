# Copyright (c) 2026 Daniel Ari Friedman
"""Operating-characteristic figures retain unavailable intervals and invalid assumptions."""

from pathlib import Path
from typing import Protocol

from matplotlib.text import Text

from thanks_for_nothing.calibration import CalibrationAudit
from thanks_for_nothing.calibration_fixtures import LABELS, Fixture
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, panels, save


class _Heading(Protocol):
    def suptitle(self, t: str, *, fontsize: float) -> Text: ...


def _heading(fig: _Heading, text: str) -> None:
    _ = fig.suptitle(text, fontsize=10)


def statistical_calibration(audit: CalibrationAudit, output: Path) -> FigureRecord:
    """Separate interval coverage from null rejection and expose bootstrap availability."""
    fig, _ = figure(6.54, 7.0)
    fig.clear()
    top, bottom = panels(fig, vertical=True)
    for offset, label, marker, role, rates in (
        (
            -0.2,
            "Percentile",
            "o",
            "positive_recall",
            [(r.coverage_rate, r.coverage_ci_low, r.coverage_ci_high) for r in audit.rows],
        ),
        (
            0.0,
            "Analytic t",
            "s",
            "matched_random_recall",
            [
                (r.analytic_t_coverage_rate, r.analytic_t_coverage_ci_low, r.analytic_t_coverage_ci_high)
                for r in audit.rows
            ],
        ),
        (
            0.2,
            "Bootstrap t",
            "D",
            "absence_appreciation",
            [
                (
                    r.studentized_coverage_rate,
                    r.studentized_coverage_ci_low,
                    r.studentized_coverage_ci_high,
                )
                for r in audit.rows
            ],
        ),
    ):
        values = [r[0] for r in rates]
        errors = [[r[0] - r[1] for r in rates], [r[2] - r[0] for r in rates]]
        _ = top.errorbar(
            values,
            [i + offset for i in range(len(rates))],
            xerr=errors,
            fmt=marker,
            capsize=2,
            color=PALETTE[role],
            label=label,
        )
    labels = [
        f"{LABELS[Fixture(r.fixture)]}\nboot-t {r.studentized_available}/{r.experiments} available"
        for r in audit.rows
    ]
    _ = top.set_yticks(range(len(audit.rows)), labels)
    _ = top.plot([1 - audit.alpha, 1 - audit.alpha], [-0.4, len(audit.rows) - 0.6], color=PALETTE["ink"])
    lower = min(
        min(r.coverage_ci_low, r.analytic_t_coverage_ci_low, r.studentized_coverage_ci_low)
        for r in audit.rows
    )
    upper = max(
        max(r.coverage_ci_high, r.analytic_t_coverage_ci_high, r.studentized_coverage_ci_high)
        for r in audit.rows
    )
    _ = top.set(
        xlim=(max(0, lower - 0.02), min(1, upper + 0.02)),
        ylim=(-1.1, len(audit.rows) - 0.5),
        xlabel="Coverage fraction: detail scale (binomial CI)",
        title="A  Interval coverage",
    )
    top.invert_yaxis()
    _ = top.legend(loc="upper center", ncol=3)
    discrete = next(r for r in audit.rows if r.fixture == Fixture.DISCRETE)
    observed_percent = 100 * discrete.studentized_available / discrete.experiments
    exact_percent = 100 * audit.discrete_availability.exact_availability
    conditional = (
        f"{100 * discrete.studentized_covered / discrete.studentized_available:.1f}%"
        if discrete.studentized_available
        else "unavailable"
    )
    _heading(
        fig,
        "\n".join(
            (
                "Rare Bernoulli bootstrap t",
                f"Exact availability: {exact_percent:.1f}%; observed: {observed_percent:.1f}%",
                f"Coverage given available: {conditional}",
            )
        ),
    )
    nulls = [r for r in audit.rows if r.true_difference == 0]
    for index, row in enumerate(nulls):
        _ = bottom.errorbar(
            row.rejection_rate,
            index,
            xerr=[
                [row.rejection_rate - row.rejection_ci_low],
                [row.rejection_ci_high - row.rejection_rate],
            ],
            fmt="o",
            capsize=3,
            color=PALETTE["ink"],
        )
    _ = bottom.axvline(audit.alpha, color=PALETTE["no_recall"], lw=1)
    _ = bottom.set_yticks(range(len(nulls)), [LABELS[Fixture(r.fixture)] for r in nulls])
    upper = max(r.rejection_ci_high for r in nulls)
    right = min(1.0, max(upper, 0.1) * 1.25)
    _ = bottom.set(
        xlim=(0, right),
        ylim=(-0.5, len(nulls)),
        xlabel="Rejection fraction (interval binomial CI)",
        title="B  Mean-zero stress tests",
    )
    bottom.invert_yaxis()
    shift = next(r for r in audit.rows if r.true_difference != 0)
    _ = bottom.text(
        0.98,
        0.02,
        f"{shift.true_difference:+g} SD shift: {shift.rejections}/{shift.experiments} detected",
        ha="right",
        transform=bottom.transAxes,
        fontsize=10,
    )
    return save(
        fig,
        output,
        "statistical_calibration",
        "Distribution-sensitive statistical calibration",
        "Coverage includes unavailable intervals as failures; skew and Bernoulli violate sign symmetry.",
        ("data/statistical_calibration.json",),
    )
