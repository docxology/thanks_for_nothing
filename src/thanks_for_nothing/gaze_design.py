# Copyright (c) 2026 Daniel Ari Friedman
"""GNN admission and native structural support for the new visual inquiry task."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.gaze_contracts import GazeDesign
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.practice_contracts import PracticeDesign
from thanks_for_nothing.practice_inference import admitted_priors
from thanks_for_nothing.specifications import AdmittedModel, load_model
from thanks_for_nothing.standalone_gnn import ModelContext, conditional_channels, conditional_model


@dataclass(frozen=True, slots=True)
class GazeTask:
    """An admitted scene with conditional channels and actual upstream family admission."""

    model: AdmittedModel
    design: GazeDesign
    structural_hash: str
    channels: FloatArray
    coordinates: FloatArray
    restricted_prior: FloatArray
    open_prior: FloatArray
    analysis: AnalysisDesign


def load_gaze_task(specification_dir: Path | None = None) -> GazeTask:
    """Reject mismatched tensors, regions, source roles and unnormalized conditional channels."""
    model = load_model("gaze", specification_dir)
    design = GazeDesign.model_validate_json(model.parameters_json)
    structural = load_model(design.structural_model, specification_dir)
    practice = PracticeDesign.model_validate_json(structural.parameters_json)
    restricted, open_prior = admitted_priors(structural, practice)
    channels = np.asarray(design.channels, dtype=np.float64)
    coordinates = np.asarray(design.coordinates, dtype=np.float64)
    canonical_a = np.asarray(model.tensors.A, dtype=np.float64)
    embedding = np.asarray(design.transfer_state_map, dtype=np.float64)
    if (
        channels.shape != (3, 3, len(open_prior))
        or not np.isfinite(channels).all()
        or ((channels <= 0) | (channels >= 1)).any()
        or np.max(abs(np.sum(channels, axis=1, dtype=np.float64) - 1)) > FINITE_PROBABILITY_TOLERANCE
        or np.max(abs(channels[:1].reshape(3, 3) - canonical_a)) > FINITE_PROBABILITY_TOLERANCE
        or np.max(abs(open_prior - np.asarray(model.tensors.D, dtype=np.float64))) != 0
        or np.asarray(model.tensors.B).shape != (3, 3, 1)
        or np.max(
            abs(
                np.asarray(model.tensors.B, dtype=np.float64).reshape(3, 3) - np.eye(3, dtype=np.float64)
            )
        )
        != 0
    ):
        message = "Gaze requires aligned canonical tensors and positive normalized region channels"
        raise ContractError(message)
    if (
        coordinates.shape != (len(design.regions), 2)
        or not np.isfinite(coordinates).all()
        or ((coordinates < 0) | (coordinates > 1)).any()
        or set(design.regions) != set(range(len(design.channels)))
        or design.initial_location >= len(design.coordinates)
        or design.trajectory_steps > min(design.steps, design.transfer_steps, design.source_steps)
        or len(set(design.conditions)) != len(design.conditions)
        or "pragmatic_restricted" not in design.conditions
        or "sham" not in design.conditions
        or "inquiry_open" not in design.conditions
        or any(design.example_window >= len(context.candidates) for context in design.contexts)
        or len({context.name for context in design.contexts}) != len(design.contexts)
        or any(
            candidate not in range(3) for context in design.contexts for candidate in context.candidates
        )
    ):
        message = "Gaze registration, contexts and paired reference conditions are invalid"
        raise ContractError(message)
    channels = channels / np.sum(channels, axis=1, keepdims=True, dtype=np.float64)
    channels[0] = np.asarray(model.tensors.A, dtype=np.float64)
    if (
        embedding.shape != (2, len(design.coordinates))
        or not np.isfinite(embedding).all()
        or (embedding < 0).any()
        or np.max(abs(np.sum(embedding, axis=0, dtype=np.float64) - 1)) > FINITE_PROBABILITY_TOLERANCE
        or not design.comparisons
        or len(set(design.comparisons)) != len(design.comparisons)
        or any(
            left == right or left not in design.conditions or right not in design.conditions
            for left, right in design.comparisons
        )
        or not design.transfer_comparisons
        or len(set(design.transfer_comparisons)) != len(design.transfer_comparisons)
        or any(left == right for left, right in design.transfer_comparisons)
    ):
        message = "Gaze requires a normalized state embedding and distinct declared paired contrasts"
        raise ContractError(message)
    open_scene = conditional_model(
        "scene_open",
        channels,
        open_prior,
        np.asarray(model.tensors.C, dtype=np.float64),
        context=ModelContext(
            (model, structural),
            "thanks_for_nothing.gaze_active:run_gaze_episode",
            "P(o|q,z), q-major/z-minor. Actions set q and preserve the candidate z.",
            initial_query=design.regions[design.initial_location],
        ),
    )
    restricted_scene = conditional_model(
        "scene_restricted",
        channels,
        restricted,
        np.asarray(model.tensors.C, dtype=np.float64),
        context=ModelContext(
            (model, structural),
            "thanks_for_nothing.gaze_active:run_gaze_episode",
            "Same scene A,B with genuinely restricted candidate support in D.",
            initial_query=design.regions[design.initial_location],
        ),
    )
    channels = conditional_channels(open_scene, len(channels))
    open_prior = np.asarray(
        np.sum(np.asarray(open_scene.tensors.D, dtype=np.float64).reshape(len(channels), -1), axis=0),
        dtype=np.float64,
    )
    restricted = np.asarray(
        np.sum(
            np.asarray(restricted_scene.tensors.D, dtype=np.float64).reshape(len(channels), -1), axis=0
        ),
        dtype=np.float64,
    )
    return GazeTask(
        model,
        design,
        structural.source_hash,
        channels,
        coordinates,
        restricted,
        open_prior,
        load_analysis(specification_dir),
    )
