# Copyright (c) 2026 Daniel Ari Friedman
"""Repeated family coverage with known means, preserved dependence and rare-event failures."""

from dataclasses import dataclass
from math import sqrt
from typing import ClassVar, Literal, assert_never

import numpy as np
from pydantic import BaseModel, ConfigDict
from scipy.stats import t
from simulation.resampling import binomial_summary

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.intervals import FloatArray
from thanks_for_nothing.joint_contracts import JointBlock, JointDesign
from thanks_for_nothing.simultaneous import joint_region

JointFixture = Literal[
    "independent_gaussian",
    "correlated_gaussian",
    "heterogeneous_gaussian",
    "centered_exponential",
    "rare_bernoulli",
]


class _BinomialBounds(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    ci_low: float
    ci_high: float


@dataclass(frozen=True, slots=True)
class CoverageRate:
    """Binomial uncertainty over independent experiments, not correlated contrast columns."""

    count: int
    total: int
    rate: float
    low: float
    high: float
    monte_carlo_se: float
    confidence: float


@dataclass(frozen=True, slots=True)
class JointCalibration:
    """Family coverage requires all six targets and counts unavailable intervals as failure."""

    fixture: str
    strata: int
    units_per_stratum: int
    contrasts: int
    joint_coverage: CoverageRate
    pointwise_family_coverage: CoverageRate
    family_availability: CoverageRate


def coverage_rate(count: int, total: int, *, confidence: float | None = None) -> CoverageRate:
    """Use the pinned Realizing Emptiness exact binomial interval for an observed rate."""
    level = 1 - load_analysis().alpha if confidence is None else confidence
    bounds = _BinomialBounds.model_validate(binomial_summary(count, total, confidence=level))
    rate = count / total
    return CoverageRate(
        count, total, rate, bounds.ci_low, bounds.ci_high, sqrt(rate * (1 - rate) / total), level
    )


def _sample(fixture: JointFixture, rng: np.random.Generator, units: int) -> FloatArray:
    match fixture:
        case "independent_gaussian":
            return rng.normal(size=(1, units, 6))
        case "correlated_gaussian":
            common = rng.normal(size=(1, units, 1))
            return sqrt(0.8) * common + sqrt(0.2) * rng.normal(size=(1, units, 6))
        case "heterogeneous_gaussian":
            scales = np.asarray([0.25, 1.0, 4.0])[:, None, None]
            return rng.normal(size=(3, units, 6)) * scales
        case "centered_exponential":
            return rng.exponential(size=(1, units, 6)) - 1
        case "rare_bernoulli":
            return np.asarray(rng.binomial(1, 0.01, size=(1, units, 6)) - 0.01, dtype=np.float64)
        case _:
            assert_never(fixture)


def _pointwise_family_covered(values: FloatArray, confidence: float) -> bool:
    strata, units, columns = len(values), len(values.swapaxes(0, 1)), len(values.T)
    mean = np.asarray(np.mean(values, axis=(0, 1), dtype=np.float64), dtype=np.float64)
    variance = np.asarray(np.var(values, axis=1, ddof=1, dtype=np.float64), dtype=np.float64) / units
    totals = np.asarray(np.sum(variance, axis=0, dtype=np.float64), dtype=np.float64)
    changes: FloatArray = values - values[:, :1, :]
    ranges = np.asarray(np.max(np.abs(changes), axis=(0, 1)), dtype=np.float64)
    if (totals <= 0).any() or not (ranges > 0).all():
        return False
    degrees = np.asarray(
        totals * totals / np.sum(variance * variance / (units - 1), axis=0), dtype=np.float64
    )
    return all(
        abs(float(np.sum(mean[index : index + 1], dtype=np.float64)))
        <= float(
            t.ppf(
                (1 + confidence) / 2,
                float(np.sum(degrees[index : index + 1], dtype=np.float64)),
            )
        )
        * sqrt(float(np.sum(totals[index : index + 1], dtype=np.float64)))
        / strata
        for index in range(columns)
    )


def calibrate_joint_regions(
    design: JointDesign, *, rate_confidence: float | None = None
) -> tuple[JointCalibration, ...]:
    """Compare joint and pointwise rectangles on identical independent mathematical samples.

    Fixture distributions and their zero means are fixed mathematical controls,
    independent of gratitude-model parameters. No coverage threshold is a gate.
    """
    fixtures: tuple[JointFixture, ...] = (
        "independent_gaussian",
        "correlated_gaussian",
        "heterogeneous_gaussian",
        "centered_exponential",
        "rare_bernoulli",
    )
    results: list[JointCalibration] = []
    level = 1 - load_analysis().alpha if rate_confidence is None else rate_confidence
    for fixture_index, fixture in enumerate(fixtures):
        rng = np.random.default_rng(np.random.SeedSequence([design.seed, 1, fixture_index]))
        covered = pointwise = available = 0
        strata = 0
        for experiment in range(design.calibration_experiments):
            values = _sample(fixture, rng, design.calibration_units)
            strata = len(values)
            trial_design = design.model_copy(
                update={
                    "seed": int(
                        np.sum(
                            np.random.SeedSequence(
                                [design.seed, fixture_index, experiment]
                            ).generate_state(1, dtype=np.uint64),
                            dtype=np.uint64,
                        )
                    ),
                    "draws": design.calibration_draws,
                }
            )
            block = JointBlock(fixture, tuple(str(i) for i in range(6)), values, (False,) * 6)
            region = joint_region((block,), trial_design)
            complete = region.status == "complete"
            available += complete
            covered += complete and all(
                row.low is not None and row.high is not None and row.low <= 0 <= row.high
                for row in region.intervals
            )
            pointwise += _pointwise_family_covered(values, design.confidence)
        n = design.calibration_experiments
        results.append(
            JointCalibration(
                fixture,
                strata,
                design.calibration_units,
                6,
                coverage_rate(covered, n, confidence=level),
                coverage_rate(pointwise, n, confidence=level),
                coverage_rate(available, n, confidence=level),
            )
        )
    return tuple(results)
