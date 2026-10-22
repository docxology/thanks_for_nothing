# Copyright (c) 2026 Daniel Ari Friedman
"""Source gaze reproduction, learned transfer and controlled representation inquiry."""

from hashlib import sha256
from pathlib import Path

import numpy as np

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.contracts import LearningExperiment
from thanks_for_nothing.finite_evidence import FINITE_PROBABILITY_TOLERANCE
from thanks_for_nothing.gaze_active import build_active_gaze
from thanks_for_nothing.gaze_contracts import (
    EVIDENCE_ORACLE_TOLERANCE,
    GazeAudit,
    GazeEpisode,
    TransferGaze,
)
from thanks_for_nothing.gaze_design import GazeTask, load_gaze_task
from thanks_for_nothing.gaze_math import float_values
from thanks_for_nothing.gaze_statistics import active_contrasts, transfer_contrasts
from thanks_for_nothing.gaze_transfer import build_transfer
from thanks_for_nothing.source_yarbus import run_yarbus_cohort


def _episode_controls(rows: tuple[GazeEpisode, ...], task: GazeTask) -> dict[str, bool]:
    index = {(row.context, row.replicate, row.window, row.condition): row for row in rows}
    groups = {(row.context, row.replicate, row.window) for row in rows}
    return {
        "active_potential_outcomes_paired": all(
            len({index[*key, condition].exposure_sha256 for condition in task.design.conditions}) == 1
            for key in groups
        ),
        "sham_exact": all(
            index[*key, "sham"].locations == index[*key, "pragmatic_restricted"].locations
            and index[*key, "sham"].observations == index[*key, "pragmatic_restricted"].observations
            and index[*key, "sham"].final_posterior
            == index[*key, "pragmatic_restricted"].final_posterior
            and index[*key, "sham"].mean_balanced_log_loss
            == index[*key, "pragmatic_restricted"].mean_balanced_log_loss
            for key in groups
        ),
        "restricted_support_preserved": all(
            all(
                value == 0
                for value, prior in zip(
                    row.final_posterior,
                    float_values(task.restricted_prior),
                    strict=True,
                )
                if prior == 0
            )
            for row in rows
            if row.condition in ("pragmatic_restricted", "inquiry_restricted", "sham")
        ),
        "native_evidence_oracle": all(
            row.native_evidence_max_error < EVIDENCE_ORACLE_TOLERANCE for row in rows
        ),
        "episode_outputs_valid": all(
            len(row.locations) == len(row.observations) == task.design.steps
            and all(0 <= value < len(task.design.coordinates) for value in row.locations)
            and all(0 <= value < len(task.model.tensors.A) for value in row.observations)
            and abs(sum(row.final_posterior) - 1) < FINITE_PROBABILITY_TOLERANCE
            and min(row.final_posterior) >= 0
            and np.isfinite(
                (
                    row.mean_balanced_log_loss,
                    row.mean_information_gain,
                    row.mean_movement_cost,
                    row.positive_occupancy,
                )
            ).all()
            for row in rows
        ),
    }


def _transfer_controls(rows: tuple[TransferGaze, ...]) -> dict[str, bool]:
    index = {(row.bridge, row.paired_id, row.condition): row for row in rows}
    ids = {(row.bridge, row.paired_id) for row in rows}
    return {
        "transfer_baselines_paired": all(
            len({row.pre_policy for row in rows if (row.bridge, row.paired_id) == identity}) == 1
            and len({row.pre_locations for row in rows if (row.bridge, row.paired_id) == identity}) == 1
            and len({row.exposure_sha256 for row in rows if (row.bridge, row.paired_id) == identity})
            == 1
            for identity in ids
        ),
        "transfer_valuation_null": all(
            index[*identity, "no_recall"].post_policy
            == index[*identity, "absence_appreciation"].post_policy
            and index[*identity, "no_recall"].post_locations
            == index[*identity, "absence_appreciation"].post_locations
            for identity in ids
        ),
        "transfer_probability_closure": all(
            abs(sum(policy) - 1) < FINITE_PROBABILITY_TOLERANCE and min(policy) > 0
            for row in rows
            for policy in (row.pre_policy, row.post_policy)
        ),
    }


def build_gaze_audit(
    experiment: LearningExperiment,
    *,
    root: Path | None = None,
    specification_dir: Path | None = None,
) -> GazeAudit:
    """Keep source replication and the two new, explicitly declared mechanisms separate."""
    task = load_gaze_task(specification_dir)
    source = run_yarbus_cohort(task.design, root)
    transfer, transfer_hashes = build_transfer(experiment, task, specification_dir)
    episodes = build_active_gaze(task)
    contrasts = (*transfer_contrasts(transfer, task), *active_contrasts(episodes, task))
    controls = {
        "source_before_rounded_reproduction": source.published_before_matches,
        **_transfer_controls(transfer),
        **_episode_controls(episodes, task),
    }
    return GazeAudit(
        "thanks_for_nothing.gaze.v1",
        task.design,
        task.model.source_hash,
        task.structural_hash,
        transfer_hashes,
        sha256(record_json(experiment.parameters).encode()).hexdigest(),
        source,
        transfer,
        episodes,
        contrasts,
        controls,
        all(controls.values()),
    )
