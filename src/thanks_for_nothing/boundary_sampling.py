# Copyright (c) 2026 Daniel Ari Friedman
"""Paired scene gaze and boundary-question episodes using actual native finite inference."""

from dataclasses import dataclass
from hashlib import sha256

import numpy as np

from thanks_for_nothing.boundary_contracts import BoundaryCondition, BoundaryEpisode, BoundaryRegime
from thanks_for_nothing.boundary_design import BoundaryTask
from thanks_for_nothing.boundary_math import (
    appearance_posterior,
    boundary_policy,
    population_regret,
    query_costs,
)
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import fit_finite_evidence
from thanks_for_nothing.gaze_math import categorical_samples, float_values
from thanks_for_nothing.inference import FloatArray


@dataclass(frozen=True, slots=True)
class BoundaryExposure:
    """Complete query-specific potential outcomes, never counted as independent subjects."""

    regime: BoundaryRegime
    scene: int
    boundary: int
    replicate: int
    actions: FloatArray
    outcomes: FloatArray
    sha256: str


def make_exposure(
    task: BoundaryTask, regime: BoundaryRegime, scene: int, boundary: int, replicate: int
) -> BoundaryExposure:
    """Seed by unit identity, so increasing N preserves every existing unit's potential outcomes."""
    if (
        scene not in range(3)
        or boundary not in range(3)
        or replicate not in range(task.design.replicates)
    ):
        message = "Boundary exposure identity is outside the declared fixed strata and replicates"
        raise ContractError(message)
    rng = np.random.default_rng(
        np.random.SeedSequence(
            [task.design.seed, task.design.regimes.index(regime), scene, boundary, replicate]
        )
    )
    actions = rng.random(task.design.steps)
    outcomes = rng.random((task.design.steps, len(task.diagnostic)))
    return BoundaryExposure(
        regime,
        scene,
        boundary,
        replicate,
        actions,
        outcomes,
        sha256(actions.tobytes() + outcomes.tobytes()).hexdigest(),
    )


def run_boundary_episode(
    task: BoundaryTask,
    exposure: BoundaryExposure,
    condition: BoundaryCondition,
    *,
    yoked_queries: tuple[int, ...] | None = None,
) -> BoundaryEpisode:
    """Sham erases action identity and ignores the demonstrator's schedule likelihood.

    This is a nonautonomous matched-query comparator; erasure does not establish
    that an adaptive demonstrator's entire schedule is information-free.
    """
    queries_count = len(task.diagnostic)
    if (
        exposure.scene not in range(3)
        or exposure.boundary not in range(3)
        or exposure.replicate not in range(task.design.replicates)
        or exposure.actions.shape != (task.design.steps,)
        or exposure.outcomes.shape != (task.design.steps, queries_count)
        or any(
            not np.isfinite(values).all() or ((values < 0) | (values >= 1)).any()
            for values in (exposure.actions, exposure.outcomes)
        )
        or exposure.sha256
        != sha256(exposure.actions.tobytes() + exposure.outcomes.tobytes()).hexdigest()
        or condition not in task.design.conditions
        or (condition == "sham") != (yoked_queries is not None)
        or (
            yoked_queries is not None
            and (
                len(yoked_queries) != task.design.steps
                or any(q not in range(queries_count) for q in yoked_queries)
            )
        )
    ):
        message = "Boundary episode requires complete paired uniforms and a valid sham schedule"
        raise ContractError(message)
    prior = task.restricted_prior if condition == "restricted" else task.open_prior
    posterior = prior.copy()
    log_likelihood = np.zeros(9, dtype=np.float64)
    channels = task.channels(exposure.regime)
    true_state = 3 * exposure.scene + exposure.boundary
    appearance = (
        task.design.scene_maps[exposure.boundary][exposure.scene]
        if exposure.regime == "diagnostic"
        else exposure.scene
    )
    queries: list[int] = []
    outcomes: list[int] = []
    scene_losses: list[float] = []
    costs: list[float] = []
    errors: list[float] = []
    location = task.gaze.design.initial_location
    for step in range(task.design.steps):
        if yoked_queries is not None:
            query = yoked_queries[step]
        else:
            policy = boundary_policy(task, posterior, location, exposure.regime, condition)
            query = int(np.sum(categorical_samples(policy, exposure.actions[step : step + 1])))
        process = channels[query : query + 1, :, true_state : true_state + 1].reshape(-1)
        uniform = exposure.outcomes[step : step + 1, query : query + 1].reshape(-1)
        outcome = int(np.sum(categorical_samples(process, uniform)))
        scene_losses.append(
            population_regret(task, appearance_posterior(task, posterior, exposure.regime), appearance)
        )
        costs.append(float(np.sum(query_costs(task, location)[query : query + 1])))
        likelihood = channels[query : query + 1, outcome : outcome + 1, :].reshape(-1)
        if condition == "sham" and query >= len(task.gaze.design.coordinates):
            response = outcome % 3
            marginal = np.asarray(
                np.sum(channels[query : query + 1].reshape(3, 3, 9), axis=0, dtype=np.float64),
                dtype=np.float64,
            )
            likelihood = marginal[response : response + 1].reshape(-1)
        log_likelihood += np.log(likelihood)
        _, posterior, _, error = fit_finite_evidence(prior, log_likelihood)
        errors.append(error)
        queries.append(query)
        outcomes.append(outcome)
        if query < len(task.gaze.design.coordinates):
            location = query
    joint = posterior.reshape(3, 3)
    scene = np.asarray(np.sum(joint, axis=1, dtype=np.float64), dtype=np.float64)
    boundary = np.asarray(np.sum(joint, axis=0, dtype=np.float64), dtype=np.float64)
    target = np.eye(3, dtype=np.float64)[exposure.boundary : exposure.boundary + 1].reshape(-1)
    return BoundaryEpisode(
        exposure.regime,
        exposure.scene,
        exposure.boundary,
        exposure.replicate,
        condition,
        exposure.sha256,
        tuple(queries),
        tuple(outcomes),
        float_values(posterior),
        float_values(scene),
        float_values(boundary),
        -float(np.sum(boundary[boundary > 0] * np.log(boundary[boundary > 0]))),
        float(np.sum((boundary - target) ** 2)),
        population_regret(task, scene, exposure.scene),
        float(np.mean(scene_losses)),
        float(np.mean(costs)),
        sum(q >= len(task.gaze.design.coordinates) for q in queries) / len(queries),
        max(errors),
    )


def sample_boundary_episodes(task: BoundaryTask) -> tuple[BoundaryEpisode, ...]:
    """Run complete six-policy pairs; adaptive sham reuses the integrated query schedule."""
    rows: list[BoundaryEpisode] = []
    for regime in task.design.regimes:
        for scene in range(3):
            for boundary in range(3):
                for replicate in range(task.design.replicates):
                    exposure = make_exposure(task, regime, scene, boundary, replicate)
                    integrated = run_boundary_episode(task, exposure, "integrated")
                    for condition in task.design.conditions:
                        if condition == "integrated":
                            rows.append(integrated)
                        elif condition == "sham":
                            rows.append(
                                run_boundary_episode(
                                    task, exposure, condition, yoked_queries=integrated.queries
                                )
                            )
                        else:
                            rows.append(run_boundary_episode(task, exposure, condition))
    return tuple(rows)
