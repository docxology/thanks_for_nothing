# Copyright (c) 2026 Daniel Ari Friedman
"""Native finite variational evidence with an independent stable scalar oracle."""

from math import exp, fsum, log
from typing import Final

import numpy as np
from formalism.models import FreeEnergyTerms

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.inference import FloatArray

FINITE_PROBABILITY_TOLERANCE: Final = 1e-12


def fit_finite_evidence(
    prior: FloatArray,
    log_likelihood: FloatArray,
) -> tuple[FreeEnergyTerms, FloatArray, float, float]:
    """Refit a supported posterior; compare imported KL-minus-accuracy with scalar evidence."""
    if (
        prior.ndim != 1
        or log_likelihood.shape != prior.shape
        or not np.isfinite(prior).all()
        or not np.isfinite(log_likelihood).all()
        or (prior < 0).any()
        or abs(float(np.sum(prior)) - 1) > FINITE_PROBABILITY_TOLERANCE
    ):
        message = "Finite evidence requires a normalized prior and finite candidate log likelihoods"
        raise ContractError(message)
    maximum = float(np.max(log_likelihood[prior > 0]))
    shifted = np.zeros_like(prior)
    support = prior > 0
    shifted[support] = prior[support] * np.exp(log_likelihood[support] - maximum)
    posterior = np.asarray(shifted / np.sum(shifted), dtype=np.float64)
    terms = FreeEnergyTerms.from_distributions(posterior, prior, log_likelihood, base=float(np.e))
    evidence = fsum(
        float(np.sum(prior[i : i + 1])) * exp(float(np.sum(log_likelihood[i : i + 1])) - maximum)
        for i in range(len(prior))
        if float(np.sum(prior[i : i + 1])) > 0
    )
    oracle = -log(evidence) - maximum
    return terms, posterior, oracle, abs(terms.free_energy - oracle)
