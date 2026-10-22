# Copyright (c) 2026 Daniel Ari Friedman
"""Exhaustive rational evidence selection and binomial operating characteristics."""

from fractions import Fraction
from math import comb, fsum, isfinite, log, log1p
from pathlib import Path
from typing import Final

import numpy as np

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.practice_contracts import (
    ExactDecisionAudit,
    ExactDecisionRow,
    ExactOperatingPoint,
    PracticeDesign,
)
from thanks_for_nothing.practice_inference import admitted_priors, compare_priors
from thanks_for_nothing.specifications import load_model

Channels = tuple[tuple[Fraction, ...], tuple[Fraction, ...]]
ORACLE_TOLERANCE: Final = 1e-10


def _rational_log(value: Fraction) -> float:
    return log(value.numerator) - log(value.denominator)


def _evidence_and_forecast(
    channels: Channels, prior: tuple[Fraction, ...], counts: tuple[int, int]
) -> tuple[Fraction, Fraction]:
    """Use exact products and sums, independently of the imported floating-point VFE path."""
    weights = tuple(
        mass * p_zero ** counts[0] * p_one ** counts[1]
        for mass, p_zero, p_one in zip(prior, *channels, strict=True)
    )
    evidence = sum(weights, Fraction())
    forecast = sum((p * w for p, w in zip(channels[0], weights, strict=True)), Fraction()) / evidence
    return evidence, forecast


def _loss(probability: float, forecast: float) -> float:
    return -probability * log(forecast) - (1 - probability) * log1p(-forecast)


def _operating_point(probability: float, rows: tuple[ExactDecisionRow, ...]) -> ExactOperatingPoint:
    n = len(rows) - 1
    p = Fraction(str(probability))
    masses = tuple(Fraction(comb(n, k)) * p**k * (1 - p) ** (n - k) for k in range(n + 1))
    open_mass = sum(
        (mass for mass, row in zip(masses, rows, strict=True) if row.supports_open), Fraction()
    )
    restricted = tuple(_loss(probability, row.restricted_forecast) for row in rows)
    selected = tuple(_loss(probability, row.evidence_selected_forecast) for row in rows)
    return ExactOperatingPoint(
        probability,
        tuple(float(mass) for mass in masses),
        str(open_mass.numerator),
        str(open_mass.denominator),
        float(open_mass),
        _rational_log(open_mass) / log(10) if open_mass else None,
        fsum(float(mass) * loss for mass, loss in zip(masses, restricted, strict=True)),
        fsum(float(mass) * loss for mass, loss in zip(masses, selected, strict=True)),
        fsum(
            float(mass) * (after - before)
            for mass, before, after in zip(masses, restricted, selected, strict=True)
        ),
        sum(masses, Fraction()) == 1,
    )


def build_exact_decision_audit(*, specification_dir: Path | None = None) -> ExactDecisionAudit:
    """Enumerate every count; probability weights use only the GNN-declared process schedules.

    Decimal strings of admitted tensor values define rational coefficients. Priors
    are normalized exactly and restricted through the upstream-admitted support.
    Decisions and binomial masses are rational; logarithms and displayed losses
    retain floating-point evaluation error. No Monte Carlo interval is involved.
    """
    model = load_model("emptiness_practice", specification_dir)
    design = PracticeDesign.model_validate_json(model.parameters_json)
    restricted, opened = admitted_priors(model, design)
    likelihood = np.asarray(model.tensors.A, dtype=np.float64)
    channels = (
        tuple(Fraction(str(p)) for p in model.tensors.A[0]),
        tuple(Fraction(str(p)) for p in model.tensors.A[1]),
    )
    raw_open = tuple(Fraction(str(p)) for p in model.tensors.D)
    active_support = tuple(
        float(np.sum(restricted[i : i + 1], dtype=np.float64)) > 0 for i in range(len(opened))
    )
    total = sum(raw_open, Fraction())
    open_prior = tuple(p / total for p in raw_open)
    restricted_mass = sum(
        (p for p, active in zip(open_prior, active_support, strict=True) if active), Fraction()
    )
    restricted_prior = tuple(
        p / restricted_mass if active else Fraction()
        for p, active in zip(open_prior, active_support, strict=True)
    )
    rows: list[ExactDecisionRow] = []
    for count in range(design.calibration_samples + 1):
        counts = (count, design.calibration_samples - count)
        z_r, forecast_r = _evidence_and_forecast(channels, restricted_prior, counts)
        z_o, forecast_o = _evidence_and_forecast(channels, open_prior, counts)
        native = compare_priors(likelihood, restricted, opened, counts)
        log_bf = _rational_log(z_o / z_r)
        selected = forecast_o if z_o > z_r else forecast_r
        rows.append(
            ExactDecisionRow(
                count,
                log_bf,
                native.log_bayes_factor,
                z_o > z_r,
                native.prefers_open,
                float(forecast_r),
                float(selected),
                max(
                    abs(log_bf - native.log_bayes_factor),
                    abs(log_bf + native.delta_free_energy),
                    abs(float(forecast_r) - native.restricted_forecast),
                    abs(float(forecast_o) - native.open_forecast),
                    native.oracle_error,
                ),
            )
        )
    probabilities = sorted({p for context in design.contexts for p in context.probabilities})
    if any(not isfinite(p) or not 0 < p < 1 for p in probabilities):
        message = "Exact operating probabilities must lie strictly between zero and one"
        raise ContractError(message)
    points = tuple(_operating_point(p, tuple(rows)) for p in probabilities)
    controls = {
        "every_calibration_count_enumerated": tuple(r.zero_count for r in rows)
        == tuple(range(design.calibration_samples + 1)),
        "rational_binomial_masses_sum_to_one": all(p.probability_total_exact for p in points),
        "native_decisions_match_rational_evidence": all(
            r.supports_open == r.native_supports_open for r in rows
        ),
        "native_vfe_and_forecasts_match_rational_oracle": max(r.numerical_max_error for r in rows)
        < ORACLE_TOLERANCE,
        "restricted_prior_is_conditional_open_prior": sum(restricted_prior, Fraction()) == 1
        and 0 < restricted_mass < 1,
    }
    return ExactDecisionAudit(
        "thanks_for_nothing.exact_decision.v1",
        model.source_hash,
        design.calibration_samples,
        float(restricted_mass),
        tuple(rows),
        points,
        controls,
        all(controls.values()),
    )
