# Copyright (c) 2026 Daniel Ari Friedman
"""Compose a joint experiment from actual GNN tensors and native structural support."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from thanks_for_nothing.boundary_contracts import BoundaryDesign, BoundaryRegime
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.gaze_design import GazeTask, load_gaze_task
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.joint_contracts import MIN_PAIRED_UNITS
from thanks_for_nothing.specifications import AdmittedModel, load_model
from thanks_for_nothing.standalone_gnn import ModelContext, conditional_channels, conditional_model


@dataclass(frozen=True, slots=True)
class BoundaryTask:
    """Nine joint states in Z-major/H-minor order; queries by outcome by joint state."""

    model: AdmittedModel
    design: BoundaryDesign
    gaze: GazeTask
    diagnostic: FloatArray
    label_only: FloatArray
    open_prior: FloatArray
    restricted_prior: FloatArray

    def channels(self, regime: BoundaryRegime) -> FloatArray:
        """Return the explicitly distinct observation regime."""
        if regime not in self.design.regimes:
            message = "Boundary observation regime is not declared"
            raise ContractError(message)
        return self.diagnostic if regime == "diagnostic" else self.label_only


def contingency_channel(reliability: float) -> FloatArray:
    """Return P(a,r|H); each marginal is uniform, while their relation depends on H."""
    if not np.isfinite(reliability) or not 1 / 3 < reliability < 1:
        message = "Contingency reliability must be strictly between chance and one"
        raise ContractError(message)
    return np.asarray(
        [
            [
                (reliability if response == (action + boundary) % 3 else (1 - reliability) / 2) / 3
                for boundary in range(3)
            ]
            for action in range(3)
            for response in range(3)
        ],
        dtype=np.float64,
    )


def _channels(gaze: GazeTask, design: BoundaryDesign, *, diagnostic: bool) -> FloatArray:
    visual = np.asarray(
        [
            [
                [
                    gaze.channels[region, outcome % 3, design.scene_maps[h][z] if diagnostic else z] / 3
                    for z in range(3)
                    for h in range(3)
                ]
                for outcome in range(9)
            ]
            for region in gaze.design.regions
        ],
        dtype=np.float64,
    )
    probes = np.asarray(
        [
            contingency_channel(reliability)[:, [0, 1, 2] * 3] if diagnostic else np.full((9, 9), 1 / 9)
            for reliability in design.probe_reliabilities
        ],
        dtype=np.float64,
    )
    channels = np.empty((len(visual) + len(probes), 9, 9), dtype=np.float64)
    channels[: len(visual)] = visual
    channels[len(visual) :] = probes
    return channels


def load_boundary_task(specification_dir: Path | None = None) -> BoundaryTask:
    """Require the declared symmetry, exact tensor composition and inherited native support."""
    model = load_model("boundary_gaze", specification_dir)
    design = BoundaryDesign.model_validate_json(model.parameters_json)
    gaze = load_gaze_task(specification_dir)
    if (
        design.scene_maps != ((0, 1, 2), (1, 2, 0), (2, 0, 1))
        or not design.probe_reliabilities
        or len(design.probe_costs) != len(design.probe_reliabilities)
        or any(not np.isfinite(cost) or cost < 0 for cost in design.probe_costs)
        or design.regimes != ("diagnostic", "label_only")
        or design.conditions
        != ("visual", "integrated", "boundary_only", "uniform", "restricted", "sham")
        or design.endpoints != ("anchored_regret", "boundary_brier")
        or design.comparisons
        != (
            ("integrated", "visual"),
            ("boundary_only", "visual"),
            ("uniform", "visual"),
            ("restricted", "visual"),
            ("sham", "visual"),
            ("integrated", "uniform"),
            ("integrated", "boundary_only"),
        )
        or tuple(sorted(set(design.prefixes))) != design.prefixes
        or min(design.prefixes) < MIN_PAIRED_UNITS
        or max(design.prefixes) != design.replicates
        or np.max(abs(gaze.open_prior - 1 / 3)) > FINITE_PROBABILITY_TOLERANCE
        or np.max(abs(gaze.restricted_prior - np.asarray([0.5, 0.5, 0.0], dtype=np.float64)))
        > FINITE_PROBABILITY_TOLERANCE
    ):
        message = "Boundary design requires declared cyclic symmetry, complete controls and prefixes"
        raise ContractError(message)
    diagnostic = _channels(gaze, design, diagnostic=True)
    label_only = _channels(gaze, design, diagnostic=False)
    opened = np.asarray(model.tensors.D, dtype=np.float64)
    if (
        np.asarray(model.tensors.A).shape != (9, 9)
        or np.asarray(model.tensors.B).shape != (9, 9, 1)
        or opened.shape != (9,)
        or np.max(abs(np.asarray(model.tensors.A, dtype=np.float64) - diagnostic[:1].reshape(9, 9)))
        > FINITE_PROBABILITY_TOLERANCE
        or np.max(abs(np.asarray(model.tensors.B).reshape(9, 9) - np.eye(9))) != 0
        or any(model.tensors.C)
        or np.max(abs(opened - np.outer(gaze.open_prior, gaze.open_prior).reshape(-1)))
        > FINITE_PROBABILITY_TOLERANCE
        or any(
            not np.isfinite(channels).all()
            or (channels <= 0).any()
            or np.max(abs(np.sum(channels, axis=1, dtype=np.float64) - 1)) > FINITE_PROBABILITY_TOLERANCE
            for channels in (diagnostic, label_only)
        )
    ):
        message = "Boundary canonical tensors must equal the admitted nine-state composition"
        raise ContractError(message)
    restricted = np.outer(gaze.open_prior, gaze.restricted_prior).reshape(-1)
    compiled = tuple(
        conditional_model(
            f"boundary_{regime}",
            channels,
            opened,
            np.asarray(model.tensors.C, dtype=np.float64),
            context=ModelContext(
                (model, gaze.model),
                "thanks_for_nothing.boundary_sampling:run_boundary_episode",
                f"{regime}: all spatial/probe queries; q-major/Z-major/H-minor basis.",
                initial_query=gaze.design.initial_location,
            ),
        )
        for regime, channels in (("diagnostic", diagnostic), ("label_only", label_only))
    )
    diagnostic, label_only = (conditional_channels(instance, len(diagnostic)) for instance in compiled)
    opened = np.asarray(
        np.sum(np.asarray(compiled[0].tensors.D, dtype=np.float64).reshape(len(diagnostic), -1), axis=0),
        dtype=np.float64,
    )
    restricted_models = tuple(
        conditional_model(
            f"boundary_{regime}_restricted",
            channels,
            restricted,
            np.asarray(model.tensors.C, dtype=np.float64),
            context=ModelContext(
                (model, gaze.model),
                "thanks_for_nothing.boundary_sampling:run_boundary_episode",
                f"{regime}: full query law with excluded-H support; q-major/Z-major/H-minor.",
                initial_query=gaze.design.initial_location,
            ),
        )
        for regime, channels in (("diagnostic", diagnostic), ("label_only", label_only))
    )
    restricted = np.asarray(
        np.sum(
            np.asarray(restricted_models[0].tensors.D, dtype=np.float64).reshape(len(diagnostic), -1),
            axis=0,
        ),
        dtype=np.float64,
    )
    return BoundaryTask(model, design, gaze, diagnostic, label_only, opened, restricted)
