# Copyright (c) 2026 Daniel Ari Friedman
"""Finite distinctions between absent harm, missing evidence and valuation."""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final

import numpy as np
from formalism.models import complexity_kl
from pydantic import BaseModel, ConfigDict, Field
from simulation.blackwell_ordering import build_blackwell_bayes_risk_audit
from typing_extensions import TypedDict

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.inference import FloatArray, posterior
from thanks_for_nothing.specifications import load_model

PROBABILITY_TOLERANCE: Final = 1e-12


class AbsenceParameters(BaseModel):
    """Counterfactual values cannot change likelihoods."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    reference_hazard: float = Field(ge=0, le=1, allow_inf_nan=False)
    harm_cost: float = Field(ge=0, allow_inf_nan=False)
    blackwell_grid_steps: int = Field(ge=2)


class AbsenceControls(TypedDict):
    """Discriminating finite semantics and imported mathematical controls."""

    missing_preserves_prior: bool
    observed_absence_informative: bool
    uninformative_no_shift: bool
    zero_reference_no_value: bool
    zero_cost_no_value: bool
    label_permutation_invariant: bool
    invalid_probability_rejected: bool
    imported_blackwell_controls: bool


@dataclass(frozen=True, slots=True)
class NothingnessAudit:
    """Operational comparators, without philosophical or clinical identity claims."""

    prior: tuple[float, ...]
    missing_posterior: tuple[float, ...]
    observed_absence_posterior: tuple[float, ...]
    missing_kl_bits: float
    observed_absence_kl_bits: float
    reference_value: float
    blackwell_original_risk: float
    blackwell_erasure_risk: float
    controls: AbsenceControls
    all_controls_pass: bool
    model_sha256: str


def counterfactual_value(reference_hazard: float, harm_cost: float, actual_cost: float = 0.0) -> float:
    """Return expected reference harm minus actual cost; this is a valuation, not evidence."""
    if (
        not all(np.isfinite(v) for v in (reference_hazard, harm_cost, actual_cost))
        or not 0 <= reference_hazard <= 1
        or min(harm_cost, actual_cost) < 0
    ):
        message = "Invalid finite counterfactual valuation"
        raise ContractError(message)
    return reference_hazard * harm_cost - actual_cost


def build_nothingness_audit(*, specification_dir: Path | None = None) -> NothingnessAudit:
    """Execute missingness, non-reification and imported Blackwell controls."""
    model = load_model("nothingness", specification_dir)
    params = AbsenceParameters.model_validate_json(model.parameters_json)
    likelihood: FloatArray = np.asarray(model.tensors.A, dtype=np.float64)
    prior: FloatArray = np.asarray(model.tensors.D, dtype=np.float64)
    absent = posterior(likelihood, prior, 0)
    missing = posterior(likelihood, prior, None)
    uninformative = posterior(
        np.full(likelihood.shape, 1 / likelihood.shape[0], dtype=np.float64), prior, 0
    )
    permuted = posterior(likelihood[:, ::-1], prior[::-1], 0)
    invalid_rejected = False
    try:
        _ = posterior(likelihood * 2, prior, 0)
    except ContractError:
        invalid_rejected = True
    blackwell = build_blackwell_bayes_risk_audit(grid_steps=params.blackwell_grid_steps)
    controls: AbsenceControls = {
        "missing_preserves_prior": bool(
            np.max(np.abs(missing - prior)) == 0 and complexity_kl(missing, prior) == 0
        ),
        "observed_absence_informative": bool(complexity_kl(absent, prior) > 0),
        "uninformative_no_shift": bool(np.max(abs(uninformative - prior)) < PROBABILITY_TOLERANCE),
        "zero_reference_no_value": counterfactual_value(0, params.harm_cost) == 0,
        "zero_cost_no_value": counterfactual_value(params.reference_hazard, 0) == 0,
        "label_permutation_invariant": bool(
            np.max(abs(permuted - absent[::-1])) < PROBABILITY_TOLERANCE
            and np.max(np.abs(likelihood @ absent - likelihood[:, ::-1] @ permuted))
            < PROBABILITY_TOLERANCE
        ),
        "invalid_probability_rejected": invalid_rejected,
        "imported_blackwell_controls": bool(blackwell["all_controls_pass"]),
    }
    return NothingnessAudit(
        tuple(float(np.sum(prior[i : i + 1])) for i in range(prior.size)),
        tuple(float(np.sum(missing[i : i + 1])) for i in range(missing.size)),
        tuple(float(np.sum(absent[i : i + 1])) for i in range(absent.size)),
        complexity_kl(missing, prior),
        complexity_kl(absent, prior),
        counterfactual_value(params.reference_hazard, params.harm_cost),
        float(blackwell["original_bayes_risk"]),
        float(blackwell["chance_risk"]),
        controls,
        all(controls.values()),
        model.source_hash,
    )
