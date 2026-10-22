# Copyright (c) 2026 Daniel Ari Friedman
"""Execute the pinned QRF and Gaussian boundary audits with independent mathematical checks."""

import inspect
import json
from dataclasses import dataclass
from hashlib import sha256
from importlib import import_module
from importlib.resources import files
from pathlib import Path
from typing import ClassVar

import numpy as np
from pydantic import BaseModel, ConfigDict
from simulation.markov_blanket import build_markov_blanket_discovery_audit
from simulation.qrf_env import boundary_channel_ledger, boundary_indistinguishability_audit

from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.provenance import file_digest


class _Profile(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    name: str


class _QRFRow(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    deployment: _Profile
    distribution_hashable: tuple[tuple[str, float], ...]


class _QRF(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    channel_count: int
    rows: tuple[_QRFRow, ...]
    all_admissible_distributions_equal: bool


class _LedgerRow(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    channel_id: str
    finite_surrogate_role: str


class _Ledger(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    rows: tuple[_LedgerRow, ...]
    controls: dict[str, bool]
    all_controls_pass: bool


class _Ensemble(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    sample_count: int
    positive_definite_count: int


class _Markov(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    precision_matrix: tuple[tuple[float, ...], ...]
    internal_nodes: tuple[int, ...]
    blanket_nodes: tuple[int, ...]
    external_nodes: tuple[int, ...]
    precision_support_f1: float
    partial_correlation_best_f1: float
    marginal_correlation_best_f1: float
    perturbation_ensemble: _Ensemble
    controls: dict[str, bool]
    all_controls_pass: bool


@dataclass(frozen=True, slots=True)
class BoundaryUpstreamAudit:
    """Finite equality and known-covariance comparator; no universal boundary-identifiability claim."""

    schema: str
    module_sha256: dict[str, str]
    specification_sha256: dict[str, str]
    raw_audit_sha256: dict[str, str]
    qrf_distributions: tuple[tuple[str, tuple[tuple[str, float], ...]], ...]
    channel_roles: tuple[tuple[str, str], ...]
    precision_matrix: tuple[tuple[float, ...], ...]
    correlation_matrix: tuple[tuple[float, ...], ...]
    internal_nodes: tuple[int, ...]
    blanket_nodes: tuple[int, ...]
    external_nodes: tuple[int, ...]
    precision_support_f1: float
    partial_correlation_best_f1: float
    upstream_marginal_best_f1: float
    exhaustive_marginal_best_f1: float
    covariance_inverse_error: float
    perturbation_samples: int
    positive_definite_samples: int
    controls: dict[str, bool]
    all_controls_pass: bool


def build_boundary_upstream() -> BoundaryUpstreamAudit:
    """Do not equate a failing marginal threshold with failure of full covariance inversion."""
    raw_qrf = boundary_indistinguishability_audit()
    raw_ledger = boundary_channel_ledger()
    raw_markov = build_markov_blanket_discovery_audit()
    qrf, ledger, graph = (
        _QRF.model_validate(raw_qrf),
        _Ledger.model_validate(raw_ledger),
        _Markov.model_validate(raw_markov),
    )
    precision = np.asarray(graph.precision_matrix, dtype=np.float64)
    covariance = np.linalg.inv(precision)
    variances = np.asarray(
        [float(np.sum(covariance[i : i + 1, i : i + 1])) for i in range(len(covariance))],
        dtype=np.float64,
    )
    correlation = covariance / np.sqrt(np.outer(variances, variances))
    reconstructed = np.linalg.inv(covariance)
    error = float(np.max(abs(reconstructed - precision)))
    scores = {
        j: float(np.max(abs(correlation[list(graph.internal_nodes), j : j + 1])))
        for j in range(len(precision))
        if j not in graph.internal_nodes
    }
    truth = set(graph.blanket_nodes)
    best = 0.0
    for threshold in [-1.0, *sorted(set(scores.values())), 1.0]:
        found = {j for j, value in scores.items() if value > threshold}
        best = max(best, 2 * len(found & truth) / (len(found) + len(truth)))
    distributions = tuple((row.deployment.name, row.distribution_hashable) for row in qrf.rows)
    probabilities = np.asarray([p for _, p in qrf.rows[0].distribution_hashable], dtype=np.float64)
    altered = probabilities.copy()
    perturbation = float(np.sum(probabilities[:1])) / 2
    altered[:1] += perturbation
    altered[1:2] -= perturbation
    controls = {
        "qrf_equal_full_distributions_recomputed": bool(
            qrf.all_admissible_distributions_equal
            and len(distributions) > 1
            and all(row[1] == distributions[0][1] for row in distributions)
        ),
        "qrf_complete_bitstring_enumeration": all(
            len(row.distribution_hashable) == 2**qrf.channel_count
            and len({bits for bits, _ in row.distribution_hashable}) == 2**qrf.channel_count
            and abs(sum(p for _, p in row.distribution_hashable) - 1) < FINITE_PROBABILITY_TOLERANCE
            for row in qrf.rows
        ),
        "normalized_alternative_detected": bool(
            (altered >= 0).all()
            and abs(float(np.sum(altered)) - 1) < FINITE_PROBABILITY_TOLERANCE
            and (abs(altered - probabilities) > 0).any()
        ),
        "channel_ledger_controls": ledger.all_controls_pass
        and bool(ledger.controls)
        and all(ledger.controls.values()),
        "gaussian_controls": graph.all_controls_pass
        and bool(graph.controls)
        and all(graph.controls.values()),
        "known_covariance_recovers_precision": error < FINITE_PROBABILITY_TOLERANCE,
        "all_marginal_threshold_intervals_fail": best < 1,
        "perturbation_denominator_retained": 0
        < graph.perturbation_ensemble.positive_definite_count
        <= graph.perturbation_ensemble.sample_count,
    }
    modules = (
        "formalism.models",
        "simulation.qrf_env",
        "simulation.markov_blanket",
        "modeling.registry",
    )
    return BoundaryUpstreamAudit(
        "thanks_for_nothing.boundary_upstream.v1",
        {name: file_digest(Path(inspect.getfile(import_module(name)))) for name in modules},
        {
            path.name: file_digest(Path(str(path)))
            for path in files("modeling").joinpath("specifications").iterdir()
            if path.name.endswith(".gnn.md")
        },
        {
            name: sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
            for name, value in (("qrf", raw_qrf), ("ledger", raw_ledger), ("markov", raw_markov))
        },
        distributions,
        tuple((row.channel_id, row.finite_surrogate_role) for row in ledger.rows),
        graph.precision_matrix,
        tuple(
            tuple(float(np.sum(correlation[i : i + 1, j : j + 1])) for j in range(len(correlation)))
            for i in range(len(correlation))
        ),
        graph.internal_nodes,
        graph.blanket_nodes,
        graph.external_nodes,
        graph.precision_support_f1,
        graph.partial_correlation_best_f1,
        graph.marginal_correlation_best_f1,
        best,
        error,
        graph.perturbation_ensemble.sample_count,
        graph.perturbation_ensemble.positive_definite_count,
        controls,
        all(controls.values()),
    )
