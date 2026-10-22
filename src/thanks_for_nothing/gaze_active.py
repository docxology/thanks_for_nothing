# Copyright (c) 2026 Daniel Ari Friedman
"""Enacted one-step visual inquiry under restricted or revisable representation families."""

from dataclasses import dataclass, replace
from hashlib import sha256
from typing import assert_never

import numpy as np

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE, fit_finite_evidence
from thanks_for_nothing.gaze_contracts import GazeCondition, GazeEpisode
from thanks_for_nothing.gaze_design import GazeTask
from thanks_for_nothing.gaze_math import (
    balanced_scene_loss,
    categorical_samples,
    float_values,
    region_prediction,
    softmax_scores,
)
from thanks_for_nothing.inference import FloatArray


@dataclass(frozen=True, slots=True)
class GazeExposure:
    """Potential outcomes indexed by fixation time and region; paired across policies."""

    context: str
    replicate: int
    window: int
    true_candidate: int
    action_uniforms: FloatArray
    outcome_uniforms: FloatArray
    sha256: str


def gaze_policy(
    task: GazeTask,
    posterior: FloatArray,
    location: int,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Separate utility, exact mutual information and movement in the declared policy."""
    if (
        posterior.shape != task.open_prior.shape
        or not np.isfinite(posterior).all()
        or (posterior < 0).any()
        or abs(float(np.sum(posterior)) - 1) > FINITE_PROBABILITY_TOLERANCE
        or not 0 <= location < len(task.design.regions)
    ):
        message = "Gaze policy requires a supported probability vector and a declared location"
        raise ContractError(message)
    prediction, information = region_prediction(task.channels, posterior)
    displacement = task.coordinates - task.coordinates[location : location + 1]
    distances: FloatArray = np.sqrt(np.sum(displacement * displacement, axis=1, dtype=np.float64))
    utility = prediction @ np.asarray(task.model.tensors.C, dtype=np.float64)
    region_scores = utility + task.design.information_weight * information
    scores: FloatArray = task.design.action_precision * (
        region_scores[list(task.design.regions)] - task.design.saccade_cost * distances
    )
    return softmax_scores(scores), information, prediction


def run_gaze_episode(
    task: GazeTask,
    exposure: GazeExposure,
    condition: GazeCondition,
) -> GazeEpisode:
    """Update from the selected region only; independently score every location before that update."""
    match condition:
        case "pragmatic_restricted" | "sham":
            initial, epistemic, uniform = task.restricted_prior, False, False
        case "pragmatic_open":
            initial, epistemic, uniform = task.open_prior, False, False
        case "inquiry_open":
            initial, epistemic, uniform = task.open_prior, True, False
        case "inquiry_restricted":
            initial, epistemic, uniform = task.restricted_prior, True, False
        case "uniform_open":
            initial, epistemic, uniform = task.open_prior, False, True
        case _:
            assert_never(condition)
    if (
        exposure.action_uniforms.shape != (task.design.steps,)
        or exposure.outcome_uniforms.shape != (task.design.steps, 3)
        or exposure.true_candidate not in range(3)
        or any(
            not np.isfinite(values).all() or ((values < 0) | (values >= 1)).any()
            for values in (exposure.action_uniforms, exposure.outcome_uniforms)
        )
    ):
        message = "Gaze exposure requires finite paired uniforms and a declared true candidate"
        raise ContractError(message)
    policy_task = (
        task
        if epistemic
        else replace(
            task,
            design=task.design.model_copy(update={"information_weight": 0.0}),
        )
    )
    posterior = initial.copy()
    log_likelihood = np.zeros_like(posterior)
    locations: list[int] = []
    observations: list[int] = []
    losses: list[float] = []
    information_values: list[float] = []
    costs: list[float] = []
    errors: list[float] = []
    previous = task.design.initial_location
    truth = task.channels[:, :, exposure.true_candidate : exposure.true_candidate + 1].reshape(3, 3)
    truth = truth.T[:, list(task.design.regions)]
    for step in range(task.design.steps):
        policy, information, prediction = gaze_policy(policy_task, posterior, previous)
        displacement = task.coordinates - task.coordinates[previous : previous + 1]
        distances: FloatArray = np.sqrt(np.sum(displacement * displacement, axis=1, dtype=np.float64))
        if uniform:
            policy = np.full(len(task.design.coordinates), 1 / len(task.design.coordinates))
        selected = int(np.sum(categorical_samples(policy, exposure.action_uniforms[step : step + 1])))
        region = task.design.regions[selected]
        process = task.channels[
            region : region + 1, :, exposure.true_candidate : exposure.true_candidate + 1
        ].reshape(-1)
        uniform_value = exposure.outcome_uniforms[step : step + 1, region : region + 1].reshape(-1)
        outcome = int(np.sum(categorical_samples(process, uniform_value)))
        losses.append(balanced_scene_loss(truth, prediction.T[:, list(task.design.regions)]))
        information_values.append(float(np.sum(information[region : region + 1])))
        costs.append(task.design.saccade_cost * float(np.sum(distances[selected : selected + 1])))
        log_likelihood += np.log(
            task.channels[region : region + 1, outcome : outcome + 1, :].reshape(-1)
        )
        _, posterior, _, error = fit_finite_evidence(initial, log_likelihood)
        errors.append(error)
        locations.append(selected)
        observations.append(outcome)
        previous = selected
    return GazeEpisode(
        exposure.context,
        exposure.replicate,
        exposure.window,
        condition,
        exposure.true_candidate,
        exposure.sha256,
        tuple(locations),
        tuple(observations),
        float_values(posterior),
        float(np.mean(losses)),
        sum(task.design.regions[v] == 0 for v in locations) / len(locations),
        float(np.mean(information_values)),
        float(np.mean(costs)),
        max(errors),
    )


def build_active_gaze(task: GazeTask) -> tuple[GazeEpisode, ...]:
    """Reset the admitted family each episode; share complete potential outcomes across conditions."""
    rows: list[GazeEpisode] = []
    for context_index, context in enumerate(task.design.contexts):
        for replicate in range(task.design.replicates):
            for window, candidate in enumerate(context.candidates):
                rng = np.random.default_rng(
                    np.random.SeedSequence(
                        [
                            task.design.seed,
                            context_index,
                            replicate,
                            window,
                        ]
                    )
                )
                actions = rng.random(task.design.steps)
                outcomes = rng.random((task.design.steps, 3))
                exposure = GazeExposure(
                    context.name,
                    replicate,
                    window,
                    candidate,
                    actions,
                    outcomes,
                    sha256(actions.tobytes() + outcomes.tobytes()).hexdigest(),
                )
                rows.extend(
                    run_gaze_episode(task, exposure, condition) for condition in task.design.conditions
                )
    return tuple(rows)
