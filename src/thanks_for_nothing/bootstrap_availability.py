# Copyright (c) 2026 Daniel Ari Friedman
"""Exact finite Bernoulli availability under the all-resamples-positive-variance rule."""

from dataclasses import dataclass
from math import exp, isfinite, log1p

from scipy.stats import binom

from thanks_for_nothing.estimation import MINIMUM_REPLICATES, StatisticalInputError


@dataclass(frozen=True, slots=True)
class CountAvailability:
    """Original-count mass and conditional resampling probabilities."""

    successes: int
    sample_probability: float
    constant_resample_probability: float
    interval_available_probability: float


@dataclass(frozen=True, slots=True)
class BernoulliAvailability:
    """Exact availability and its complete count-wise decomposition."""

    sample_size: int
    probability: float
    draws: int
    counts: tuple[CountAvailability, ...]
    exact_availability: float


def bernoulli_availability(sample_size: int, probability: float, draws: int) -> BernoulliAvailability:
    """Integrate conditional empirical-bootstrap availability over the original binomial count.

    An interval requires a nonconstant original sample and no constant draw among
    B independent size-n resamples. This is availability, not interval coverage.
    """
    if type(sample_size) is not int or sample_size < MINIMUM_REPLICATES:
        field = "sample_size"
        raise StatisticalInputError(field, "integer >= 2 required")
    if type(draws) is not int or draws < 1:
        field = "draws"
        raise StatisticalInputError(field, "positive integer required")
    if not isfinite(probability) or not 0 <= probability <= 1:
        field = "probability"
        raise StatisticalInputError(field, "finite value in [0,1] required")
    counts: list[CountAvailability] = []
    for successes in range(sample_size + 1):
        proportion = successes / sample_size
        constant = proportion**sample_size + (1 - proportion) ** sample_size
        available = exp(draws * log1p(-constant)) if 0 < successes < sample_size else 0.0
        counts.append(
            CountAvailability(
                successes,
                float(binom.pmf(successes, sample_size, probability)),
                constant,
                available,
            )
        )
    return BernoulliAvailability(
        sample_size,
        probability,
        draws,
        tuple(counts),
        sum(row.sample_probability * row.interval_available_probability for row in counts),
    )
