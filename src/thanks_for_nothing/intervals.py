# Copyright (c) 2026 Daniel Ari Friedman
"""Stratified mean intervals with explicit studentization failure states."""

from dataclasses import dataclass
from math import sqrt
from typing import Final, Literal

import numpy as np
from numpy.typing import NDArray
from scipy.stats import t

from thanks_for_nothing.analysis_design import load_analysis

FloatArray = NDArray[np.float64]
INTERPOLATION_MIDPOINT: Final = 0.5


@dataclass(frozen=True, slots=True)
class StudentizedInterval:
    """Bootstrap t interval; zero-variance draws are counted, never discarded."""

    low: float | None
    high: float | None
    status: Literal["available", "degenerate_sample", "degenerate_resamples"]
    degenerate_resamples: int
    draws: int


@dataclass(frozen=True, slots=True)
class MeanIntervals:
    """Three pointwise intervals for one equally weighted fixed-stratum mean."""

    mean: float
    percentile_low: float
    percentile_high: float
    analytic_low: float
    analytic_high: float
    standard_error: float
    degrees_freedom: float | None
    studentized: StudentizedInterval
    confidence: float


def quantile_pair(values: FloatArray, probabilities: tuple[float, float]) -> tuple[float, float]:
    """Inclusive linear order-statistic quantiles, checked against NumPy."""
    ordered = values.copy()
    ordered.sort()
    bounds: list[float] = []
    for probability in probabilities:
        location = (len(ordered) - 1) * probability
        lower = int(location)
        upper = min(lower + 1, len(ordered) - 1)
        fraction = location - lower
        left = float(np.sum(ordered[lower : lower + 1]))
        right = float(np.sum(ordered[upper : upper + 1]))
        bounds.append(
            left + (right - left) * fraction
            if fraction < INTERPOLATION_MIDPOINT
            else right - (right - left) * (1 - fraction)
        )
    return bounds[0], bounds[1]


def mean_intervals(
    data: FloatArray, draws: int, rng: np.random.Generator, *, confidence: float | None = None
) -> MeanIntervals:
    """Resample complete paired units within each admitted, equally weighted stratum.

    The analytic comparator uses Welch-Satterthwaite degrees of freedom. The
    bootstrap t root uses each resample's own within-stratum variance estimate.
    Neither interval has a universal finite-sample coverage guarantee.
    """
    level = 1 - load_analysis().alpha if confidence is None else confidence
    if not 0 < level < 1:
        message = "Interval confidence must lie strictly between zero and one"
        raise ValueError(message)
    tail = (1 - level) / 2
    probabilities = (tail, 1 - tail)
    strata, replicates = len(data), len(data.T)
    indices = rng.integers(replicates, size=(draws, strata, replicates))
    origins = data[:, :1]
    centered = data - origins
    origin = float(np.mean(origins, dtype=np.float64))
    resampled = np.take_along_axis(centered[None, :, :], indices, axis=2)
    means = np.asarray(np.mean(resampled, axis=(1, 2), dtype=np.float64), dtype=np.float64)
    centered_mean = float(np.mean(centered, dtype=np.float64))
    mean = origin + centered_mean
    low, high = quantile_pair(means, probabilities)
    low, high = origin + low, origin + high
    variances = (
        np.asarray(np.var(centered, axis=1, ddof=1, dtype=np.float64), dtype=np.float64) / replicates
    )
    total = float(np.sum(variances))
    standard_error = sqrt(total) / strata
    degrees = total * total / float(np.sum(variances * variances / (replicates - 1))) if total else None
    margin = float(t.ppf(1 - tail, degrees)) * standard_error if degrees is not None else 0.0
    resample_variances = np.asarray(
        np.var(resampled - resampled[:, :, :1], axis=2, ddof=1, dtype=np.float64),
        dtype=np.float64,
    )
    resample_totals = np.asarray(
        np.sum(resample_variances / replicates, axis=1, dtype=np.float64), dtype=np.float64
    )
    resample_se = np.asarray(np.sqrt(resample_totals) / strata, dtype=np.float64)
    zeros = int(np.sum(resample_se <= 0, dtype=np.int64))
    if total == 0:
        studentized = StudentizedInterval(None, None, "degenerate_sample", zeros, draws)
    elif zeros:
        studentized = StudentizedInterval(None, None, "degenerate_resamples", zeros, draws)
    else:
        pivots = np.asarray((means - centered_mean) / resample_se, dtype=np.float64)
        pivot_low, pivot_high = quantile_pair(pivots, probabilities)
        studentized = StudentizedInterval(
            mean - pivot_high * standard_error,
            mean - pivot_low * standard_error,
            "available",
            zeros,
            draws,
        )
    return MeanIntervals(
        mean, low, high, mean - margin, mean + margin, standard_error, degrees, studentized, level
    )
