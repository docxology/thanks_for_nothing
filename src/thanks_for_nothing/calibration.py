# Copyright (c) 2026 Daniel Ari Friedman
"""Distribution-sensitive operating characteristics with retained failures."""

from dataclasses import dataclass
from math import sqrt
from typing import ClassVar, Final, assert_never

import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from simulation.resampling import binomial_summary

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.bootstrap_availability import BernoulliAvailability, bernoulli_availability
from thanks_for_nothing.calibration_fixtures import (
    BERNOULLI_PROBABILITY,
    SYMMETRY,
    TRUE_MEAN,
    Fixture,
    sample_fixture,
)
from thanks_for_nothing.contracts import Design, StudyDesign
from thanks_for_nothing.estimation import exact_sign_flip
from thanks_for_nothing.statistics import paired_contrast

CONTROL_NAMES: Final = frozenset(
    {
        "exact_null_retained",
        "positive_control_detected",
        "seeded_control_replays",
        "exhaustive_sign_oracle",
        "constant_studentization_unavailable",
    }
)


class _RateInterval(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    ci_low: float = Field(ge=0, le=1)
    ci_high: float = Field(ge=0, le=1)


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Finite repeated-experiment rejection and coverage rates with uncertainty."""

    fixture: str
    true_difference: float
    experiments: int
    sample_size: int
    rejections: int
    rejection_rate: float
    rejection_ci_low: float
    rejection_ci_high: float
    covered: int
    coverage_rate: float
    coverage_ci_low: float
    coverage_ci_high: float
    analytic_t_covered: int
    analytic_t_coverage_rate: float
    analytic_t_coverage_ci_low: float
    analytic_t_coverage_ci_high: float
    strata: int
    sign_flip_assumption: str
    studentized_available: int
    studentized_covered: int
    studentized_coverage_rate: float
    studentized_coverage_ci_low: float
    studentized_coverage_ci_high: float
    rejection_mcse: float
    coverage_mcse: float


@dataclass(frozen=True, slots=True)
class CalibrationAudit:
    """Synthetic null and shift controls with explicit empirical evidence limits."""

    schema: str
    seed: int
    alpha: float
    bootstrap_draws: int
    permutation_draws: int
    rows: tuple[OperatingPoint, ...]
    controls: dict[str, bool]
    evidence_ceiling: str
    discrete_availability: BernoulliAvailability


def _operating_point(
    fixture: Fixture, design: StudyDesign, rng: np.random.Generator, analysis: AnalysisDesign
) -> OperatingPoint:
    seed = design.seed + analysis.calibration_seed_offset
    shift = TRUE_MEAN[fixture]
    rejections = covered = analytic_covered = studentized_covered = available = 0
    strata = 0
    for i in range(design.calibration_replicates):
        values = sample_fixture(fixture, rng, design.calibration_sample_size)
        strata = len(values)
        estimate = paired_contrast(
            values,
            seed=seed + i,
            bootstrap_draws=design.calibration_bootstrap_draws,
            permutation_draws=design.calibration_permutation_draws,
            analysis=analysis,
        )
        rejections += estimate.p_value <= analysis.alpha
        covered += estimate.ci95_low <= shift <= estimate.ci95_high
        analytic_covered += estimate.analytic_t_ci95_low <= shift <= estimate.analytic_t_ci95_high
        interval = estimate.studentized
        if interval.low is not None and interval.high is not None:
            available += 1
            studentized_covered += interval.low <= shift <= interval.high
    n = design.calibration_replicates
    rejection_ci = _RateInterval.model_validate(
        binomial_summary(rejections, n, confidence=1 - analysis.alpha)
    )
    coverage_ci = _RateInterval.model_validate(
        binomial_summary(covered, n, confidence=1 - analysis.alpha)
    )
    analytic_ci = _RateInterval.model_validate(
        binomial_summary(analytic_covered, n, confidence=1 - analysis.alpha)
    )
    studentized_ci = _RateInterval.model_validate(
        binomial_summary(studentized_covered, n, confidence=1 - analysis.alpha)
    )
    return OperatingPoint(
        fixture,
        shift,
        n,
        design.calibration_sample_size,
        rejections,
        rejections / n,
        rejection_ci.ci_low,
        rejection_ci.ci_high,
        covered,
        covered / n,
        coverage_ci.ci_low,
        coverage_ci.ci_high,
        analytic_covered,
        analytic_covered / n,
        analytic_ci.ci_low,
        analytic_ci.ci_high,
        strata,
        SYMMETRY[fixture],
        available,
        studentized_covered,
        studentized_covered / n,
        studentized_ci.ci_low,
        studentized_ci.ci_high,
        sqrt((rejections / n) * (1 - rejections / n) / n),
        sqrt((covered / n) * (1 - covered / n) / n),
    )


def build_calibration_audit(
    design: StudyDesign, *, analysis: AnalysisDesign | None = None
) -> CalibrationAudit:
    """Compare methods on identical draws; unavailable intervals count as noncoverage.

    Distribution shapes are independent mathematical stressors. Skewed fixtures
    intentionally violate sign-flip symmetry despite having zero mean.
    """
    protocol = load_analysis() if analysis is None else analysis
    seed = design.seed + protocol.calibration_seed_offset
    rng = np.random.default_rng(seed)
    rows = tuple(_operating_point(fixture, design, rng, protocol) for fixture in Fixture)
    kwargs = {
        "seed": seed,
        "bootstrap_draws": design.calibration_bootstrap_draws,
        "permutation_draws": design.calibration_permutation_draws,
    }
    null = paired_contrast([[0.0] * design.calibration_sample_size], analysis=protocol, **kwargs)
    positive = paired_contrast([[1.0] * design.calibration_sample_size], analysis=protocol, **kwargs)
    repeated = paired_contrast([[1.0] * design.calibration_sample_size], analysis=protocol, **kwargs)
    return CalibrationAudit(
        "thanks_for_nothing.statistical_calibration.v3",
        seed,
        protocol.alpha,
        design.calibration_bootstrap_draws,
        design.calibration_permutation_draws,
        rows,
        {
            "exact_null_retained": null.mean_difference == 0 and null.p_value == 1,
            "positive_control_detected": positive.mean_difference == 1
            and positive.p_value < protocol.alpha,
            "seeded_control_replays": positive == repeated,
            "exhaustive_sign_oracle": exact_sign_flip([[1.0, 2.0, 3.0]]) == 2 / 8,
            "constant_studentization_unavailable": positive.studentized.low is None,
        },
        (
            "Synthetic operating characteristics, with skew/discreteness stressors and explicit "
            "studentized availability; neither empirical power nor validation of human gratitude."
        ),
        bernoulli_availability(
            design.calibration_sample_size,
            BERNOULLI_PROBABILITY,
            design.calibration_bootstrap_draws,
        ),
    )


def calibration_consistent(
    audit: CalibrationAudit, design: Design, *, analysis: AnalysisDesign | None = None
) -> bool:
    """Bind fixture identity, denominators and exact rate intervals to the admitted design."""
    protocol = load_analysis() if analysis is None else analysis
    if (
        audit.seed != design.seed + protocol.calibration_seed_offset
        or audit.alpha != protocol.alpha
        or audit.bootstrap_draws != design.calibration_bootstrap_draws
        or audit.permutation_draws != design.calibration_permutation_draws
        or set(audit.controls) != set(CONTROL_NAMES)
        or not all(audit.controls.values())
        or tuple(row.fixture for row in audit.rows) != tuple(f.value for f in Fixture)
        or audit.discrete_availability
        != bernoulli_availability(
            design.calibration_sample_size,
            BERNOULLI_PROBABILITY,
            design.calibration_bootstrap_draws,
        )
    ):
        return False
    for fixture, row in zip(Fixture, audit.rows, strict=True):
        match fixture:
            case Fixture.HETEROGENEOUS:
                strata = 5
            case Fixture.GAUSSIAN | Fixture.SHIFT | Fixture.HEAVY_TAIL | Fixture.SKEW | Fixture.DISCRETE:
                strata = 1
            case _:
                assert_never(fixture)
        n = design.calibration_replicates
        if (
            row.experiments != n
            or row.sample_size != design.calibration_sample_size
            or row.strata != strata
            or row.true_difference != TRUE_MEAN[fixture]
            or row.sign_flip_assumption != SYMMETRY[fixture]
            or not 0 <= row.studentized_covered <= row.studentized_available <= n
        ):
            return False
        for count, rate, low, high in (
            (row.rejections, row.rejection_rate, row.rejection_ci_low, row.rejection_ci_high),
            (row.covered, row.coverage_rate, row.coverage_ci_low, row.coverage_ci_high),
            (
                row.analytic_t_covered,
                row.analytic_t_coverage_rate,
                row.analytic_t_coverage_ci_low,
                row.analytic_t_coverage_ci_high,
            ),
            (
                row.studentized_covered,
                row.studentized_coverage_rate,
                row.studentized_coverage_ci_low,
                row.studentized_coverage_ci_high,
            ),
        ):
            if not 0 <= count <= n:
                return False
            interval = _RateInterval.model_validate(
                binomial_summary(count, n, confidence=1 - audit.alpha)
            )
            if (rate, low, high) != (count / n, interval.ci_low, interval.ci_high):
                return False
        if row.rejection_mcse != sqrt(
            row.rejection_rate * (1 - row.rejection_rate) / n
        ) or row.coverage_mcse != sqrt(row.coverage_rate * (1 - row.coverage_rate) / n):
            return False
    return True
