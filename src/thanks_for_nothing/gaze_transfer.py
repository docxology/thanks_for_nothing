# Copyright (c) 2026 Daniel Ari Friedman
"""Two explicit transfer mechanisms: trained likelihoods and assessed posterior readouts."""

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from thanks_for_nothing.attention import AttentionParameters
from thanks_for_nothing.contracts import ContractError, LearningExperiment
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.gaze_contracts import TransferBridge, TransferGaze
from thanks_for_nothing.gaze_design import GazeTask
from thanks_for_nothing.gaze_math import (
    balanced_scene_loss,
    categorical_samples,
    float_values,
    integer_values,
    softmax_scores,
)
from thanks_for_nothing.specifications import Tensors, load_model
from thanks_for_nothing.standalone_gnn import ModelContext, standalone_model

if TYPE_CHECKING:
    from thanks_for_nothing.inference import FloatArray


def build_transfer(
    experiment: LearningExperiment,
    task: GazeTask,
    specification_dir: Path | None = None,
) -> tuple[tuple[TransferGaze, ...], tuple[str, ...]]:
    """Keep direct parameter transfer distinct from an assessment-readout projection."""
    study = experiment.study
    positive = load_model("attention_positive", specification_dir)
    negative = load_model("attention_negative", specification_dir)
    params = AttentionParameters.model_validate_json(positive.parameters_json)
    other = AttentionParameters.model_validate_json(negative.parameters_json)
    truth = np.asarray(params.process_likelihood, dtype=np.float64)
    if any(stratum not in study.design.luckiness for stratum in task.design.example_strata):
        message = "Declared gaze example strata must exist in the paired learning study"
        raise ContractError(message)
    if (
        params != other
        or positive.tensors.C != negative.tensors.C
        or truth.shape != (len(task.model.tensors.A), len(task.design.coordinates))
        or not np.isfinite(truth).all()
        or (truth <= 0).any()
        or np.max(abs(np.sum(truth, axis=0, dtype=np.float64) - 1)) > FINITE_PROBABILITY_TOLERANCE
    ):
        message = "Transfer requires matched attention endpoints and a common positive scene process"
        raise ContractError(message)
    index = {(row.paired_id, row.condition): row for row in experiment.parameters}
    if (
        len(index) != len(experiment.parameters)
        or len(index) != len(study.rows)
        or set(index) != {(row.paired_id, row.condition) for row in study.rows}
        or any(
            left not in {row.condition.value for row in study.rows}
            or right not in {row.condition.value for row in study.rows}
            for left, right in task.design.transfer_comparisons
        )
    ):
        message = (
            "Transfer requires complete, unique training parameters and declared comparison conditions"
        )
        raise ContractError(message)
    endpoints = (np.asarray(positive.tensors.A), np.asarray(negative.tensors.A))
    embedding_model = standalone_model(
        "transfer_embedding",
        Tensors.model_validate(
            {
                "A": task.design.transfer_state_map,
                "B": positive.tensors.B,
                "C": np.zeros(len(task.design.transfer_state_map)),
                "D": positive.tensors.D,
            }
        ),
        context=ModelContext(
            (task.model, positive),
            "thanks_for_nothing.gaze_transfer:build_transfer",
            "P(learned-state basis|location). This is a transfer embedding, not a world posterior.",
        ),
    )
    embedding = np.asarray(embedding_model.tensors.A, dtype=np.float64)
    preferences = np.asarray(task.model.tensors.C, dtype=np.float64)
    rows: list[TransferGaze] = []
    for row in study.rows:
        learned = index[row.paired_id, row.condition]
        matrices = (np.asarray(learned.pre), np.asarray(learned.post))
        if (
            learned.exposure_sha256 != row.exposure_sha256
            or learned.luckiness != row.luckiness
            or learned.replicate != row.replicate
        ) or any(
            matrix.shape != (3, 2)
            or not np.isfinite(matrix).all()
            or (matrix <= 0).any()
            or np.max(abs(np.sum(matrix, axis=0, dtype=np.float64) - 1)) > FINITE_PROBABILITY_TOLERANCE
            for matrix in matrices
        ):
            message = "Transfer training channels must be positive, normalized and exposure-bound"
            raise ContractError(message)
        stratum = study.design.luckiness.index(row.luckiness)
        rng = np.random.default_rng(np.random.SeedSequence([task.design.seed, stratum, row.replicate]))
        uniforms = rng.random(task.design.transfer_steps - 1)
        readout_channels = tuple(
            probability * endpoints[0] + (1 - probability) * endpoints[1]
            for probability in (row.pre_world_well, row.post_world_well)
        )
        mechanisms: tuple[tuple[TransferBridge, tuple[FloatArray, ...]], ...] = (
            ("likelihood", tuple(matrix @ embedding for matrix in matrices)),
            ("posterior_readout", readout_channels),
        )
        for bridge, channels in mechanisms:
            policies: list[tuple[float, ...]] = []
            locations: list[tuple[int, ...]] = []
            losses: list[float] = []
            for channel in channels:
                entropy = -np.sum(channel * np.log(channel), axis=0, dtype=np.float64)
                scores = task.design.transfer_precision * (
                    preferences @ channel - task.design.transfer_ambiguity_weight * entropy
                )
                policy = softmax_scores(scores)
                policies.append(float_values(policy))
                locations.append(
                    (
                        task.design.initial_location,
                        *integer_values(categorical_samples(policy, uniforms)),
                    )
                )
                losses.append(balanced_scene_loss(truth, channel))
            rows.append(
                TransferGaze(
                    bridge,
                    row.condition.value,
                    row.luckiness,
                    row.replicate,
                    row.paired_id,
                    row.exposure_sha256,
                    row.pre_world_well,
                    row.post_world_well,
                    policies[0],
                    policies[1],
                    locations[0],
                    locations[1],
                    sum(policies[1][i] - policies[0][i] for i in params.positive_locations),
                    losses[1] - losses[0],
                )
            )
    return tuple(rows), (positive.source_hash, negative.source_hash)
