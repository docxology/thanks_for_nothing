# Copyright (c) 2026 Daniel Ari Friedman
"""Known-answer and discriminating controls for enacted model revisability."""

from typing import Final

import numpy as np

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.practice_contracts import PracticeDesign, PracticeRow
from thanks_for_nothing.practice_inference import admitted_priors, compare_priors, practice_probability
from thanks_for_nothing.specifications import AdmittedModel

ORACLE_TOLERANCE: Final = 1e-10
PERMUTATION_TOLERANCE: Final = 1e-12


def practice_controls(
    model: AdmittedModel,
    design: PracticeDesign,
    rows: tuple[PracticeRow, ...],
) -> dict[str, bool]:
    """Retain useful restrictions, permit evidence-driven change, and expose semantic nulls."""
    restricted = np.array([1.0, 0.0], dtype=np.float64)
    open_prior = np.array([0.5, 0.5], dtype=np.float64)
    channel = np.array([[0.9, 0.1], [0.1, 0.9]], dtype=np.float64)
    useful = compare_priors(channel, restricted, open_prior, (24, 0))
    contradicted = compare_priors(channel, restricted, open_prior, (0, 24))
    tied = compare_priors(
        np.full((2, 3), 0.5, dtype=np.float64),
        np.array([0.5, 0.5, 0.0], dtype=np.float64),
        np.full(3, 1 / 3, dtype=np.float64),
        (12, 12),
    )
    invalid = False
    try:
        _ = compare_priors(channel * 2, restricted, open_prior, (24, 0))
    except ContractError:
        invalid = True
    indexed = {(r.context, r.replicate, r.window, r.condition): r for r in rows}
    paired, no_access, sham, policy = True, True, True, True
    for row in rows:
        baseline = indexed[row.context, row.replicate, row.window, "rigid"]
        paired &= row.exposure_sha256 == baseline.exposure_sha256
        if row.condition == "no_access":
            no_access &= row.forecast == baseline.forecast and not row.effective_access
        if row.condition == "sham":
            sham &= row.forecast == baseline.forecast and not row.effective_access
        if row.condition != "rigid":
            prior = (
                indexed[row.context, row.replicate, row.window - 1, row.condition]
                if row.window
                else None
            )
            expected_gain = (
                max(0.0, prior.comparison.log_bayes_factor)
                if prior is not None and prior.effective_access
                else prior.previous_observed_gain
                if prior is not None
                else 0.0
            )
            preference = 0.0 if row.condition == "no_preference" else design.examinability_preference
            policy &= row.previous_observed_gain == expected_gain and row.action_probability == (
                practice_probability(design, preference, expected_gain)
            )
    actual_restricted, actual_open = admitted_priors(model, design)
    likelihood = np.asarray(model.tensors.A, dtype=np.float64)
    permutation = np.arange(len(actual_open))[::-1]
    original = compare_priors(likelihood, actual_restricted, actual_open, (12, 12))
    permuted = compare_priors(
        likelihood[:, permutation], actual_restricted[permutation], actual_open[permutation], (12, 12)
    )
    return {
        "exact_vfe_matches_evidence_sum": max(r.comparison.oracle_error for r in rows)
        < ORACLE_TOLERANCE,
        "useful_prior_retained": not useful.prefers_open,
        "contradicted_prior_revisable": contradicted.prefers_open,
        "equal_likelihood_tie_retains_prior": tied.log_bayes_factor == 0 and not tied.prefers_open,
        "invalid_channel_rejected": invalid,
        "paired_exposures": paired,
        "no_access_preserves_forecasts": no_access,
        "sham_preserves_forecasts": sham,
        "policy_uses_previous_observed_gain_only": policy,
        "candidate_permutation_invariant": (
            abs(original.open_forecast - permuted.open_forecast) < PERMUTATION_TOLERANCE
        ),
        "preference_changes_initial_policy": (
            design.examinability_preference == 0
            or practice_probability(design, 0, 0)
            < practice_probability(design, design.examinability_preference, 0)
        ),
    }
