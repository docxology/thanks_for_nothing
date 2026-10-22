# Copyright (c) 2026 Daniel Ari Friedman
"""Explicit categorical inference, Dirichlet learning and held-out scoring."""

from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

from thanks_for_nothing.contracts import ContractError

MATRIX_DIMENSIONS: Final = 2

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]

PROBABILITY_TOLERANCE: Final = 1e-8


def cumulative(values: FloatArray, axis: int | None = None) -> FloatArray:
    """Return native cumulative sums; axis=None flattens into a typed float64 buffer."""
    output = np.empty(values.size, dtype=np.float64) if axis is None else np.empty_like(values)
    return values.cumsum(axis=axis, out=output)


def posterior(
    likelihood: FloatArray, prior: FloatArray, observation: int | None, *, precision: float = 1.0
) -> FloatArray:
    """Generalized Bayes: q(s) ∝ prior(s) A[o,s]**precision, no column renormalization."""
    if (
        likelihood.ndim != MATRIX_DIMENSIONS
        or prior.shape != (likelihood.shape[1],)
        or not np.isfinite(likelihood).all()
        or not np.isfinite(prior).all()
        or (likelihood < 0).any()
        or (prior < 0).any()
        or np.max(np.abs(np.sum(likelihood, axis=0, dtype=np.float64) - 1)) >= PROBABILITY_TOLERANCE
        or abs(float(np.sum(prior)) - 1) >= PROBABILITY_TOLERANCE
        or not np.isfinite(precision)
        or precision <= 0
    ):
        message = "Invalid categorical likelihood, prior or precision"
        raise ContractError(message)
    if observation is None:
        return prior.copy()
    if not 0 <= observation < likelihood.shape[0]:
        message = "Observation outside declared alphabet"
        raise ContractError(message)
    weights = prior * likelihood[observation : observation + 1].reshape(-1) ** precision
    if np.sum(weights) <= 0:
        message = "Observation has no support under the prior"
        raise ContractError(message)
    return weights / np.sum(weights)


def normalize_counts(counts: FloatArray) -> FloatArray:
    """Normalize proper positive Dirichlet pseudocounts columnwise."""
    if counts.ndim != MATRIX_DIMENSIONS or not np.isfinite(counts).all() or (counts <= 0).any():
        message = "Dirichlet pseudocounts must be strictly positive"
        raise ContractError(message)
    return counts / np.sum(counts, axis=0, keepdims=True, dtype=np.float64)


def learn(
    counts: FloatArray, observation: int, belief: FloatArray, rate: float, forgetting: float
) -> FloatArray:
    """Return a new count matrix; caller owns the mutable training accumulator."""
    updated = counts * forgetting
    updated[observation] += rate * belief
    return updated


def frozen_likelihood(counts: FloatArray) -> tuple[tuple[float, ...], ...]:
    """Retain normalized training parameters independently of mutable count accumulators."""
    matrix = normalize_counts(counts)
    return tuple(
        tuple(float(np.sum(matrix[i : i + 1, j : j + 1])) for j in range(len(matrix.T)))
        for i in range(len(matrix))
    )


@dataclass(frozen=True, slots=True)
class Scores:
    """Binary Brier, observation predictive log loss, and posterior entropy."""

    world_well: float
    brier: float
    nll: float
    entropy: float


def score(likelihood: FloatArray, prior: FloatArray, observations: IntArray, states: IntArray) -> Scores:
    """Evaluate frozen parameters on independent paired observations and true states."""
    if (
        observations.ndim != 1
        or states.ndim != 1
        or observations.shape != states.shape
        or not observations.size
    ):
        message = "Scoring requires matched nonempty observation and state vectors"
        raise ContractError(message)
    categories = np.unique(observations)
    category_beliefs: FloatArray = np.asarray(
        [
            posterior(likelihood, prior, int(np.sum(categories[i : i + 1])))
            for i in range(categories.size)
        ],
        dtype=np.float64,
    )
    beliefs: FloatArray = category_beliefs[np.searchsorted(categories, observations)]
    predictive = likelihood @ prior
    entropy = np.sum(
        beliefs * np.log(np.maximum(beliefs, np.finfo(float).tiny)), axis=1, dtype=np.float64
    )
    return Scores(
        float(np.mean(beliefs[:, 0])),
        float(np.mean((beliefs[:, :1].reshape(-1) - (abs(states) <= 0)) ** 2)),
        float(-np.mean(np.log(predictive.take(observations)))),
        float(-np.mean(entropy)),
    )


def optimism(well_probability: float, priors: FloatArray, well: FloatArray, poor: FloatArray) -> float:
    """Average good-news upward minus bad-news downward update, integrating latent mode."""
    changes: list[float] = []
    for index in range(priors.size):
        p = float(np.sum(priors[index : index + 1]))
        prior = np.array([p, 1 - p])
        updates: list[float] = []
        for news in (0, 1):
            q = well_probability * float(np.sum(posterior(well, prior, news)[:1])) + (
                1 - well_probability
            ) * float(np.sum(posterior(poor, prior, news)[:1]))
            updates.append(q - p)
        changes.append(updates[0] + updates[1])
    return float(np.mean(changes))
