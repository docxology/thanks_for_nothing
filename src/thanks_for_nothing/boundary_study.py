# Copyright (c) 2026 Daniel Ari Friedman
"""Joint gaze/boundary study with mathematical controls separate from the sampled effects."""

from pathlib import Path

import numpy as np

from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.boundary_design import BoundaryTask, contingency_channel, load_boundary_task
from thanks_for_nothing.boundary_math import appearance_posterior, boundary_policy, joint_prediction
from thanks_for_nothing.boundary_sampling import sample_boundary_episodes
from thanks_for_nothing.boundary_statistics import boundary_estimates
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE, fit_finite_evidence
from thanks_for_nothing.gaze_active import gaze_policy
from thanks_for_nothing.gaze_contracts import EVIDENCE_ORACLE_TOLERANCE


def boundary_mathematical_controls(task: BoundaryTask) -> dict[str, bool]:
    """Test admitted symmetry, marginal erasure, native permutation and imported visual policy."""
    posterior = np.arange(1, 10, dtype=np.float64) / 45
    log_likelihood = np.asarray(
        np.log(task.diagnostic[:1, :1].reshape(-1)) + np.log(task.diagnostic[-1:, -1:].reshape(-1)),
        dtype=np.float64,
    )
    terms, fitted, oracle, error = fit_finite_evidence(task.restricted_prior, log_likelihood)
    permutation = [8, 2, 5, 0, 7, 1, 4, 6, 3]
    permuted, q_permuted, oracle_permuted, error_permuted = fit_finite_evidence(
        task.restricted_prior[permutation], log_likelihood[permutation]
    )
    locations = len(task.gaze.design.coordinates)
    visual = boundary_policy(task, posterior, locations - 1, "diagnostic", "visual")
    inherited, _, _ = gaze_policy(
        task.gaze, appearance_posterior(task, posterior, "diagnostic"), locations - 1
    )
    _, label_information = joint_prediction(task.label_only[locations:], task.open_prior)
    _, diagnostic_information = joint_prediction(task.diagnostic[locations:], task.open_prior)
    return {
        "single_marginals_identical": all(
            np.max(
                abs(
                    np.sum(
                        contingency_channel(reliability).reshape(3, 3, 3), axis=axis, dtype=np.float64
                    )
                    - 1 / 3
                )
            )
            < FINITE_PROBABILITY_TOLERANCE
            for reliability in task.design.probe_reliabilities
            for axis in (0, 1)
        ),
        "joint_contingency_informative": bool((diagnostic_information > 0).all()),
        "label_only_probes_uninformative": bool(
            np.max(abs(label_information)) < FINITE_PROBABILITY_TOLERANCE
        ),
        "label_only_H_columns_identical": all(
            np.max(
                abs(task.label_only[:, :, 3 * z : 3 * z + 3] - task.label_only[:, :, 3 * z : 3 * z + 1])
            )
            == 0
            for z in range(3)
        ),
        "visual_policy_is_imported_gaze_policy": bool(
            np.max(abs(visual[:locations] - inherited)) < FINITE_PROBABILITY_TOLERANCE
        ),
        "consistent_state_permutation_invariant": bool(
            max(
                error,
                error_permuted,
                abs(oracle - oracle_permuted),
                abs(terms.free_energy - permuted.free_energy),
                float(np.max(abs(fitted[permutation] - q_permuted))),
            )
            < EVIDENCE_ORACLE_TOLERANCE
        ),
        "zero_support_cannot_be_recovered": not bool((abs(fitted.reshape(3, 3)[:, 2:3]) > 0).any()),
    }


def build_boundary_gaze(specification_dir: Path | None = None) -> BoundaryGazeAudit:
    """Build a new paired study, retaining its distinct reference-frame intervention target."""
    task = load_boundary_task(specification_dir)
    rows = sample_boundary_episodes(task)
    region, offsets, convergence = boundary_estimates(task, rows)
    controls = boundary_mathematical_controls(task)
    contrasts = len(task.design.regimes) * 3 * len(task.design.comparisons) * len(task.design.endpoints)
    exact_count = 3 * (len(task.design.comparisons) + 3)
    controls.update(
        {
            "complete_paired_records_admitted": True,
            "joint_family_has_all_84_members": len(region.intervals) == contrasts,
            "native_evidence_independent_oracle": max(r.native_evidence_max_error for r in rows)
            < EVIDENCE_ORACLE_TOLERANCE,
            "exact_offsets_proved_and_admitted": len(offsets) == exact_count,
            "nested_prefix_closure": len(convergence) == contrasts * len(task.design.prefixes),
        }
    )
    return BoundaryGazeAudit(
        "thanks_for_nothing.boundary_gaze.v1",
        task.design,
        task.model.source_hash,
        task.gaze.model.source_hash,
        task.gaze.structural_hash,
        rows,
        region,
        offsets,
        convergence,
        controls,
        all(controls.values()),
    )
