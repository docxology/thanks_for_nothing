# Copyright (c) 2026 Daniel Ari Friedman
"""Complete paired blocks, proved constant offsets and nested independent-sample convergence."""

from dataclasses import replace
from math import sqrt

import numpy as np

from thanks_for_nothing.boundary_contracts import (
    BoundaryCondition,
    BoundaryConvergence,
    BoundaryEndpoint,
    BoundaryEpisode,
    BoundaryRegime,
)
from thanks_for_nothing.boundary_design import BoundaryTask
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.joint_contracts import JointBlock, JointRegion
from thanks_for_nothing.simultaneous import joint_region


def admit_boundary_records(task: BoundaryTask, rows: tuple[BoundaryEpisode, ...]) -> None:
    """Reject incomplete pairs and forged exact-identity records before statistical estimation."""
    indexed = {(r.regime, r.scene, r.boundary, r.replicate, r.condition): r for r in rows}
    expected = {
        (regime, z, h, rep, condition)
        for regime in task.design.regimes
        for z in range(3)
        for h in range(3)
        for rep in range(task.design.replicates)
        for condition in task.design.conditions
    }
    if set(indexed) != expected or len(indexed) != len(rows):
        message = "Boundary records require the complete unique regime/scene/boundary/replicate grid"
        raise ContractError(message)
    for row in rows:
        identity = (row.regime, row.scene, row.boundary, row.replicate)
        visual, integrated = indexed[*identity, "visual"], indexed[*identity, "integrated"]
        joint = np.asarray(row.final_joint, dtype=np.float64)
        boundary = np.asarray(row.final_boundary, dtype=np.float64)
        scene = np.asarray(row.final_scene, dtype=np.float64)
        numbers = (
            row.boundary_entropy,
            row.boundary_brier,
            row.anchored_regret,
            row.mean_scene_regret,
            row.mean_cost,
            row.boundary_query_fraction,
            row.native_evidence_max_error,
        )
        if (
            joint.shape != (9,)
            or boundary.shape != (3,)
            or scene.shape != (3,)
            or not np.isfinite(joint).all()
            or (joint < 0).any()
            or abs(float(np.sum(joint)) - 1) > FINITE_PROBABILITY_TOLERANCE
            or np.max(abs(np.sum(joint.reshape(3, 3), axis=0, dtype=np.float64) - boundary))
            > FINITE_PROBABILITY_TOLERANCE
            or np.max(abs(np.sum(joint.reshape(3, 3), axis=1, dtype=np.float64) - scene))
            > FINITE_PROBABILITY_TOLERANCE
            or not np.isfinite(numbers).all()
            or min(numbers) < -FINITE_PROBABILITY_TOLERANCE
            or row.boundary_brier > 2 + FINITE_PROBABILITY_TOLERANCE
            or row.boundary_query_fraction > 1
            or len(row.queries) != task.design.steps
            or len(row.outcomes) != task.design.steps
            or any(q not in range(len(task.diagnostic)) for q in row.queries)
            or any(o not in range(9) for o in row.outcomes)
            or row.exposure_sha256 != visual.exposure_sha256
            or (row.condition == "restricted" and (abs(joint.reshape(3, 3)[:, 2:3]) > 0).any())
            or (
                row.condition == "sham"
                and (row.queries, row.outcomes, row.mean_cost)
                != (integrated.queries, integrated.outcomes, integrated.mean_cost)
            )
        ):
            message = "Boundary records violate probability, pairing, support or matched-query contracts"
            raise ContractError(message)
        expected_h = (
            task.gaze.restricted_prior if row.condition == "restricted" else task.gaze.open_prior
        )
        unchanged = row.regime == "label_only" or row.condition in ("visual", "sham")
        truth = np.eye(3)[row.boundary : row.boundary + 1].reshape(-1)
        if (unchanged and np.max(abs(boundary - expected_h)) > FINITE_PROBABILITY_TOLERANCE) or abs(
            row.boundary_brier - float(np.sum((boundary - truth) ** 2))
        ) > FINITE_PROBABILITY_TOLERANCE:
            message = "Boundary exact posterior/Brier identity is violated by supplied records"
            raise ContractError(message)
        if (
            row.regime == "diagnostic"
            and row.condition in ("visual", "sham", "boundary_only")
            and np.max(abs(scene - 1 / 3)) > FINITE_PROBABILITY_TOLERANCE
        ):
            message = "Diagnostic marginal scene symmetry is violated by supplied records"
            raise ContractError(message)


def _values(
    rows: tuple[BoundaryEpisode, ...],
    task: BoundaryTask,
    regime: BoundaryRegime,
    boundary: int,
    contrast: tuple[BoundaryCondition, BoundaryCondition, BoundaryEndpoint],
) -> FloatArray:
    condition, reference, endpoint = contrast
    indexed = {
        (r.scene, r.replicate, r.condition): r
        for r in rows
        if (r.regime, r.boundary) == (regime, boundary)
    }
    return np.asarray(
        [
            [
                getattr(indexed[z, rep, condition], endpoint)
                - getattr(indexed[z, rep, reference], endpoint)
                for rep in range(task.design.replicates)
            ]
            for z in range(3)
        ],
        dtype=np.float64,
    )


def _offset(
    task: BoundaryTask,
    regime: BoundaryRegime,
    boundary: int,
    comparison: tuple[BoundaryCondition, BoundaryCondition],
    endpoint: BoundaryEndpoint,
) -> float | None:
    condition, reference = comparison
    if (
        endpoint == "anchored_regret"
        and regime == "diagnostic"
        and condition in ("boundary_only", "sham")
        and reference == "visual"
    ):
        return 0.0
    if endpoint != "boundary_brier" or (
        regime != "label_only" and (condition, reference) != ("sham", "visual")
    ):
        return None
    target = np.eye(3)[boundary : boundary + 1].reshape(-1)
    prior = task.gaze.restricted_prior if condition == "restricted" else task.gaze.open_prior
    reference_prior = task.gaze.restricted_prior if reference == "restricted" else task.gaze.open_prior
    return float(np.sum((prior - target) ** 2) - np.sum((reference_prior - target) ** 2))


def boundary_estimates(
    task: BoundaryTask, rows: tuple[BoundaryEpisode, ...]
) -> tuple[JointRegion, tuple[tuple[str, float], ...], tuple[BoundaryConvergence, ...]]:
    """Translate only proved mechanism constants; other zero-variance samples remain unavailable.

    Each regime/H block has three fixed Z strata and independent paired replicate
    vectors. All blocks share one maximum-root bootstrap family. Known nonzero
    constants are subtracted before exact-zero admission and restored afterward.
    """
    admit_boundary_records(task, rows)
    blocks: list[JointBlock] = []
    offsets: dict[str, float] = {}
    convergence: list[BoundaryConvergence] = []
    for regime in task.design.regimes:
        for boundary in range(3):
            keys: list[str] = []
            columns: list[FloatArray] = []
            exact: list[bool] = []
            for condition, reference in task.design.comparisons:
                for endpoint in task.design.endpoints:
                    key = f"{regime}/H{boundary}/{condition}/{reference}/{endpoint}"
                    values = _values(rows, task, regime, boundary, (condition, reference, endpoint))
                    offset = _offset(task, regime, boundary, (condition, reference), endpoint)
                    if (
                        offset is not None
                        and np.max(abs(values - offset)) > FINITE_PROBABILITY_TOLERANCE
                    ):
                        message = "A proved boundary Brier offset fails at the paired-unit level"
                        raise ContractError(message)
                    for prefix in task.design.prefixes:
                        sample = values[:, :prefix]
                        se = (
                            sqrt(
                                float(
                                    np.sum(
                                        np.asarray(
                                            np.var(
                                                sample - sample[:, :1],
                                                axis=1,
                                                ddof=1,
                                                dtype=np.float64,
                                            ),
                                            dtype=np.float64,
                                        )
                                        / prefix,
                                        dtype=np.float64,
                                    )
                                )
                            )
                            / 3
                            if offset is None
                            else 0.0
                        )
                        convergence.append(
                            BoundaryConvergence(
                                regime,
                                boundary,
                                condition,
                                reference,
                                endpoint,
                                prefix,
                                float(np.mean(sample)) if offset is None else offset,
                                se,
                            )
                        )
                    keys.append(key)
                    exact.append(offset is not None)
                    columns.append(values if offset is None else np.zeros_like(values))
                    if offset is not None:
                        offsets[key] = offset
            values = np.asarray(columns, dtype=np.float64).transpose(1, 2, 0)
            blocks.append(JointBlock(f"{regime}/H{boundary}", tuple(keys), values, tuple(exact)))
    design = task.gaze.design.joint.model_copy(update={"seed": task.design.joint_seed})
    residual = joint_region(tuple(blocks), design)
    restored = tuple(
        replace(row, mean=offsets[row.key], low=offsets[row.key], high=offsets[row.key])
        if row.key in offsets
        else row
        for row in residual.intervals
    )
    return replace(residual, intervals=restored), tuple(offsets.items()), tuple(convergence)
