# Copyright (c) 2026 Daniel Ari Friedman
"""Exact information, proper population scores and imported gaze utility on joint states."""

import numpy as np

from thanks_for_nothing.boundary_contracts import BoundaryCondition, BoundaryRegime
from thanks_for_nothing.boundary_design import BoundaryTask
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.gaze_math import softmax_scores
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.joint_contracts import BLOCK_DIMENSIONS


def joint_prediction(channels: FloatArray, posterior: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Compute P(outcome|query) and exact I((Z,H);outcome|query), in nats."""
    if (
        channels.ndim != BLOCK_DIMENSIONS
        or posterior.shape != channels.shape[2:]
        or not np.isfinite(channels).all()
        or not np.isfinite(posterior).all()
        or (channels <= 0).any()
        or (posterior < 0).any()
        or np.max(abs(np.sum(channels, axis=1, dtype=np.float64) - 1)) > FINITE_PROBABILITY_TOLERANCE
        or abs(float(np.sum(posterior)) - 1) > FINITE_PROBABILITY_TOLERANCE
    ):
        message = "Joint prediction requires positive normalized channels and a supported posterior"
        raise ContractError(message)
    prediction = np.asarray(channels @ posterior, dtype=np.float64)
    information = np.asarray(
        np.sum(channels * posterior * (np.log(channels) - np.log(prediction)[:, :, None]), axis=(1, 2)),
        dtype=np.float64,
    )
    return prediction, information


def appearance_posterior(
    task: BoundaryTask, posterior: FloatArray, regime: BoundaryRegime
) -> FloatArray:
    """Push the joint posterior through the declared reference-to-appearance map."""
    result = np.zeros(3, dtype=np.float64)
    for z in range(3):
        for h in range(3):
            appearance = task.design.scene_maps[h][z] if regime == "diagnostic" else z
            result[appearance] += float(np.sum(posterior[3 * z + h : 3 * z + h + 1]))
    return result


def population_regret(task: BoundaryTask, posterior: FloatArray, truth: int) -> float:
    """Excess expected log loss across all locations, relative to the true channel; nats/outcome."""
    if (
        posterior.shape != (3,)
        or not np.isfinite(posterior).all()
        or (posterior < 0).any()
        or abs(float(np.sum(posterior)) - 1) > FINITE_PROBABILITY_TOLERANCE
        or truth not in range(3)
    ):
        message = "Population regret requires a normalized scene posterior and supported truth"
        raise ContractError(message)
    prediction = np.asarray(task.gaze.channels @ posterior, dtype=np.float64)
    true_channel = task.gaze.channels[:, :, truth : truth + 1].reshape(3, 3)
    regional = np.asarray(
        np.sum(true_channel * np.log(true_channel / prediction), axis=1, dtype=np.float64),
        dtype=np.float64,
    )
    return float(np.mean(regional[list(task.gaze.design.regions)], dtype=np.float64))


def query_costs(task: BoundaryTask, location: int) -> FloatArray:
    """Combine spatial movement costs with separately declared boundary-query costs."""
    displacement = task.gaze.coordinates - task.gaze.coordinates[location : location + 1]
    movement = task.gaze.design.saccade_cost * np.sqrt(
        np.sum(displacement * displacement, axis=1, dtype=np.float64)
    )
    costs = np.empty(len(task.diagnostic), dtype=np.float64)
    locations = len(task.gaze.design.coordinates)
    costs[:locations] = movement
    costs[locations:] = task.design.probe_costs
    return costs


def boundary_policy(
    task: BoundaryTask,
    posterior: FloatArray,
    location: int,
    regime: BoundaryRegime,
    condition: BoundaryCondition,
) -> FloatArray:
    """Score joint information once; use actual gaze utility, precision and geometry."""
    if (
        not 0 <= location < len(task.gaze.design.coordinates)
        or condition == "sham"
        or condition not in task.design.conditions
    ):
        message = "An autonomous boundary policy needs a visual location and a non-sham condition"
        raise ContractError(message)
    prediction, information = joint_prediction(task.channels(regime), posterior)
    utility = np.zeros(len(prediction), dtype=np.float64)
    locations = len(task.gaze.design.coordinates)
    utility[:locations] = np.sum(
        prediction[:locations].reshape(locations, 3, 3), axis=1, dtype=np.float64
    ) @ np.asarray(task.gaze.model.tensors.C, dtype=np.float64)
    scores = task.gaze.design.action_precision * (
        utility + task.gaze.design.information_weight * information - query_costs(task, location)
    )
    if condition == "uniform":
        return np.full(len(prediction), 1 / len(prediction))
    allowed = np.arange(len(prediction))
    if condition == "visual":
        allowed = allowed[:locations]
    elif condition == "boundary_only":
        allowed = allowed[locations:]
    policy = np.zeros_like(scores)
    policy[allowed] = softmax_scores(scores[allowed])
    return policy
