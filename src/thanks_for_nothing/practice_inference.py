# Copyright (c) 2026 Daniel Ari Friedman
"""Realizing Emptiness QRF admission and exact finite prior comparison in nats."""

from math import exp
from typing import Final

import numpy as np
from formalism.models import (
    BMRComparison,
    BoundaryScreen,
    QRFDeployment,
    SeparationPrior,
)

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import fit_finite_evidence
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.practice_contracts import PracticeDesign, PriorComparison
from thanks_for_nothing.specifications import AdmittedModel
from thanks_for_nothing.standalone_gnn import ModelContext, standalone_model

MATRIX_DIMENSIONS: Final = 2
PROBABILITY_TOLERANCE: Final = 1e-12


def admitted_priors(model: AdmittedModel, design: PracticeDesign) -> tuple[FloatArray, FloatArray]:
    """Use upstream structural admission; no hand-added complexity penalty or precision formula."""
    likelihood = np.asarray(model.tensors.A, dtype=np.float64)
    candidates = design.deployments
    if likelihood.shape != (2, len(candidates)) or ((likelihood <= 0) | (likelihood >= 1)).any():
        message = "Practice requires positive binary channels over all declared deployments"
        raise ContractError(message)
    transitions: FloatArray = np.asarray(model.tensors.B, dtype=np.float64)
    if transitions.shape != (len(candidates), len(candidates), 1):
        message = "Practice requires one identity transition action"
        raise ContractError(message)
    identity_difference: FloatArray = transitions[:, :, 0] - np.eye(len(candidates), dtype=np.float64)
    if float(np.max(abs(identity_difference))) != 0 or any(model.tensors.C):
        message = "Practice requires identity transitions and neutral observation preferences"
        raise ContractError(message)
    screen = BoundaryScreen(
        len(candidates[0].labels), tuple(f"b{i}" for i in range(len(candidates[0].labels)))
    )
    deployments = tuple(
        QRFDeployment(item.name, item.labels, design.metacognitive_access, design.prior_precision)
        for item in candidates
    )
    for deployment in deployments:
        deployment.validate(screen)
    accepted = SeparationPrior(design.prior_precision).admissible(deployments)
    mask = np.asarray([item in accepted for item in deployments], dtype=np.float64)
    open_prior = np.asarray(model.tensors.D, dtype=np.float64)
    restricted = open_prior * mask
    if (
        not 0 < int(np.sum(restricted > 0, dtype=np.int64)) < len(candidates)
        or (open_prior <= 0).any()
        or len({item.name for item in candidates}) != len(candidates)
    ):
        message = "Practice requires distinct candidates, open support and a proper restricted subset"
        raise ContractError(message)
    compiled = standalone_model(
        "practice_restricted",
        model.tensors.model_copy(update={"D": tuple(restricted / np.sum(restricted))}),
        context=ModelContext(
            (model,),
            "thanks_for_nothing.practice_inference:compare_priors",
            "Finite deployment A with restricted D admitted by Realizing Emptiness.",
        ),
    )
    return np.asarray(compiled.tensors.D, dtype=np.float64), open_prior


def compare_priors(
    likelihood: FloatArray, restricted: FloatArray, open_prior: FloatArray, counts: tuple[int, int]
) -> PriorComparison:
    """Compare nested-support priors with refitted posteriors and an independent evidence sum.

    This uses the upstream BMRComparison difference algebra, not its posterior-reuse
    identity: expanding support requires inference under both candidate priors.
    """
    if (
        likelihood.ndim != MATRIX_DIMENSIONS
        or restricted.ndim != 1
        or open_prior.ndim != 1
        or likelihood.shape != (2, len(restricted))
        or open_prior.shape != restricted.shape
        or len(counts) != MATRIX_DIMENSIONS
        or any(type(count) is not int or count < 0 for count in counts)
        or not np.isfinite(likelihood).all()
        or ((likelihood <= 0) | (likelihood >= 1)).any()
        or float(np.max(abs(np.sum(likelihood, axis=0, dtype=np.float64) - 1))) > PROBABILITY_TOLERANCE
        or any(
            not np.isfinite(p).all()
            or (p < 0).any()
            or abs(float(np.sum(p)) - 1) > PROBABILITY_TOLERANCE
            for p in (restricted, open_prior)
        )
    ):
        message = "Invalid finite prior-comparison inputs"
        raise ContractError(message)
    ll = np.asarray(np.asarray(counts, dtype=np.float64) @ np.log(likelihood), dtype=np.float64)
    restricted_terms, q_restricted, negative_log_evidence_r, error_r = fit_finite_evidence(
        restricted, ll
    )
    open_terms, q_open, negative_log_evidence_o, error_o = fit_finite_evidence(open_prior, ll)
    comparison = BMRComparison(restricted_terms, open_terms)
    log_bayes_factor = negative_log_evidence_r - negative_log_evidence_o
    return PriorComparison(
        restricted_terms.free_energy,
        open_terms.free_energy,
        comparison.delta_complexity,
        comparison.delta_accuracy,
        comparison.delta_free_energy,
        float(np.sum(likelihood[:1] * q_restricted)),
        float(np.sum(likelihood[:1] * q_open)),
        max(error_r, error_o),
        log_bayes_factor,
        log_bayes_factor > 0,
    )


def practice_probability(design: PracticeDesign, preference: float, previous_gain: float) -> float:
    """Choose inquiry using declared value, cost and only previously observed evidence gain."""
    if (
        not np.isfinite(preference)
        or not np.isfinite(previous_gain)
        or min(preference, previous_gain) < 0
    ):
        message = "Practice preference and previously observed gain must be finite and nonnegative"
        raise ContractError(message)
    utility = design.action_precision * (
        preference - design.practice_cost + design.previous_gain_weight * previous_gain
    )
    return 1 / (1 + exp(-utility)) if utility >= 0 else exp(utility) / (1 + exp(utility))
