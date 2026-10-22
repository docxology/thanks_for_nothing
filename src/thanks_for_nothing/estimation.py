# Copyright (c) 2026 Daniel Ari Friedman
"""Paired simulation contrasts conditional on a fixed grid of world parameters.

Independent simulated agents are resampled within each stratum. Time steps are
never counted as independent observations. Sign-flip inference additionally
requires symmetry/exchangeability of paired differences under its null.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING, ClassVar, Final

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field
from simulation.resampling import binomial_summary
from typing_extensions import override

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.intervals import StudentizedInterval, mean_intervals

if TYPE_CHECKING:
    from collections.abc import Sequence


FloatArray = NDArray[np.float64]


MATRIX_DIMENSIONS: Final = 2


MINIMUM_REPLICATES: Final = 2
MAX_EXACT_UNITS: Final = 16


@dataclass(frozen=True, slots=True)
class StatisticalInputError(ValueError):
    """Invalid paired-design or statistical input with a named field."""

    field: str
    requirement: str

    @override
    def __str__(self) -> str:
        return f"{self.field}: {self.requirement}"


class _BinomialInterval(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, allow_inf_nan=False)
    ci_low: float = Field(ge=0, le=1)
    ci_high: float = Field(ge=0, le=1)


@dataclass(frozen=True, slots=True)
class PairedEstimate:
    """Paired effect and finite Monte Carlo uncertainty for a fixed grid."""

    mean_difference: float
    ci95_low: float
    ci95_high: float
    standard_deviation: float
    cohen_dz: float | None
    positive_fraction: float
    tied_fraction: float
    p_value: float
    permutation_exceedances: int
    permutation_draws: int
    p_resolution: float
    mc_tail_ci_low: float
    mc_tail_ci_high: float
    mc_interval_confidence: float
    strata: int
    replicates_per_stratum: int
    analytic_t_ci95_low: float
    analytic_t_ci95_high: float
    analytic_t_standard_error: float
    analytic_t_degrees_freedom: float | None
    studentized: StudentizedInterval
    confidence: float


def _count(value: int, field: str, minimum: int = 1) -> None:
    if type(value) is not int or value < minimum:
        raise StatisticalInputError(field, f"integer >= {minimum} required")


def _matrix(values: Sequence[Sequence[float]] | FloatArray) -> FloatArray:
    data = np.asarray(values, dtype=np.float64)
    if data.ndim != MATRIX_DIMENSIONS or data.shape[0] < 1 or data.shape[1] < MINIMUM_REPLICATES:
        msg = "differences"
        raise StatisticalInputError(msg, "nonempty strata with at least two paired agents each")
    if not np.isfinite(data).all():
        msg = "differences"
        raise StatisticalInputError(msg, "finite values required")
    return data


def paired_contrast(  # noqa: PLR0913 - Independent seed, draw budgets and family protocol are explicit.
    differences: Sequence[Sequence[float]] | FloatArray,
    *,
    seed: int,
    bootstrap_draws: int,
    permutation_draws: int,
    family_size: int = 1,
    analysis: AnalysisDesign | None = None,
) -> PairedEstimate:
    """Estimate an equally weighted stratum mean with paired Monte Carlo inference.

    The percentile interval resamples complete agents separately within each
    fixed stratum. A plus-one two-sided sign-flip test reports its finite
    resolution and a simultaneous-family Clopper-Pearson Monte Carlo interval.
    """
    protocol = load_analysis() if analysis is None else analysis
    data = _matrix(differences)
    for value, field in (
        (bootstrap_draws, "bootstrap_draws"),
        (permutation_draws, "permutation_draws"),
        (family_size, "family_size"),
    ):
        _count(value, field)
    _count(seed, "seed", 0)
    strata, replicates = len(data), len(data.T)
    rng = np.random.default_rng(seed)
    intervals = mean_intervals(data, bootstrap_draws, rng, confidence=1 - protocol.alpha)
    mean = intervals.mean
    signs = 2 * rng.integers(0, 2, size=(permutation_draws, strata, replicates), dtype=np.int8) - 1
    null_statistics = abs(
        np.asarray(np.mean(signs * data, axis=(1, 2), dtype=np.float64), dtype=np.float64)
    )
    tolerance = 32 * np.finfo(float).eps * abs(mean)
    hits = int(np.sum(null_statistics >= abs(mean) - tolerance, dtype=np.int64))
    confidence = 1 - protocol.alpha / family_size
    interval = _BinomialInterval.model_validate(
        binomial_summary(hits, permutation_draws, confidence=confidence)
    )
    sd = float(np.std(data.reshape(-1), ddof=1))
    dz = mean / sd if sd > 0 else (0.0 if mean == 0 else None)
    return PairedEstimate(
        mean,
        intervals.percentile_low,
        intervals.percentile_high,
        sd,
        dz,
        float(np.mean(data > 0)),
        float(np.mean(abs(data) <= 0)),
        (hits + 1) / (permutation_draws + 1),
        hits,
        permutation_draws,
        1 / (permutation_draws + 1),
        interval.ci_low,
        interval.ci_high,
        confidence,
        strata,
        replicates,
        intervals.analytic_low,
        intervals.analytic_high,
        intervals.standard_error,
        intervals.degrees_freedom,
        intervals.studentized,
        intervals.confidence,
    )


def holm_adjust(p_values: Sequence[float]) -> tuple[float, ...]:
    """Apply monotone Holm correction and restore the original hypothesis order."""
    values: FloatArray = np.asarray(p_values, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        msg = "p_values"
        raise StatisticalInputError(msg, "a nonempty finite vector required")
    if ((values < 0) | (values > 1)).any():
        msg = "p_values"
        raise StatisticalInputError(msg, "probabilities in [0, 1] required")
    probabilities = [float(np.sum(values[i : i + 1])) for i in range(values.size)]
    order = sorted(range(len(probabilities)), key=probabilities.__getitem__)
    adjusted = [0.0] * len(probabilities)
    running_max = 0.0
    for rank, index in enumerate(order):
        running_max = max(running_max, probabilities[index] * (len(probabilities) - rank))
        adjusted[index] = min(1.0, running_max)
    return tuple(adjusted)


def exact_sign_flip(differences: Sequence[Sequence[float]] | FloatArray) -> float:
    """Enumerate every sign assignment as a small-sample mathematical oracle."""
    data = _matrix(differences)
    if data.size > MAX_EXACT_UNITS:
        field = "differences"
        raise StatisticalInputError(field, "at most 16 units for exhaustive enumeration")
    signs = np.asarray(tuple(product((-1.0, 1.0), repeat=data.size)), dtype=np.float64)
    observed = abs(float(np.mean(data)))
    statistics = abs(np.asarray(np.mean(signs * data.reshape(-1), axis=1), dtype=np.float64))
    tolerance = 32 * np.finfo(float).eps * observed
    return float(np.mean(statistics >= observed - tolerance))
