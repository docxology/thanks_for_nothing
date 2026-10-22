# Copyright (c) 2026 Daniel Ari Friedman
"""Categorical visual prediction, mutual information and balanced scene risk."""

import numpy as np

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.inference import FloatArray, IntArray, cumulative


def softmax_scores(scores: FloatArray) -> FloatArray:
    """Normalize finite log weights without overflow."""
    weights: FloatArray = np.exp(scores - np.max(scores))
    return np.asarray(weights / np.sum(weights), dtype=np.float64)


def categorical_samples(policy: FloatArray, uniforms: FloatArray) -> IntArray:
    """Inverse-CDF sampling retains the caller's paired common random numbers."""
    if (
        policy.ndim != 1
        or not policy.size
        or uniforms.ndim != 1
        or not np.isfinite(policy).all()
        or (policy < 0).any()
        or abs(float(np.sum(policy)) - 1) > FINITE_PROBABILITY_TOLERANCE
        or not np.isfinite(uniforms).all()
        or ((uniforms < 0) | (uniforms >= 1)).any()
    ):
        message = "Categorical sampling requires a probability vector and uniforms in [0,1)"
        raise ContractError(message)
    cdf = cumulative(policy)
    cdf[-1] = 1
    return np.asarray(np.sum(uniforms[:, None] >= cdf[None, :], axis=1, dtype=np.int64))


def float_values(values: FloatArray) -> tuple[float, ...]:
    """Freeze a numerical vector for typed JSON records without scalar dtype erasure."""
    return tuple(float(np.sum(values[i : i + 1], dtype=np.float64)) for i in range(len(values)))


def integer_values(values: IntArray) -> tuple[int, ...]:
    """Freeze sampled indices for typed JSON records without scalar dtype erasure."""
    return tuple(int(np.sum(values[i : i + 1], dtype=np.int64)) for i in range(len(values)))


def region_prediction(channels: FloatArray, posterior: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Return outcome predictions and exact expected information gain in nats per region."""
    prediction = np.asarray(channels @ posterior, dtype=np.float64)
    entropy = -np.sum(prediction * np.log(prediction), axis=1, dtype=np.float64)
    conditional = -np.sum(channels * np.log(channels), axis=1, dtype=np.float64) @ posterior
    information = np.asarray(entropy - conditional, dtype=np.float64)
    return prediction, np.maximum(information, 0)


def balanced_scene_loss(truth: FloatArray, prediction: FloatArray) -> float:
    """Exact expected log loss, equally weighted across locations rather than sampled fixations."""
    return -float(np.mean(np.sum(truth * np.log(prediction), axis=0, dtype=np.float64)))
