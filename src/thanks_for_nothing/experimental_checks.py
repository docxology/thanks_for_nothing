# Copyright (c) 2026 Daniel Ari Friedman
"""Admit experimental records separately from their ordered, short-circuit replay gates."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from pydantic import TypeAdapter

from thanks_for_nothing.artifact_checks import Gate, read_record
from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.boundary_study import build_boundary_gaze
from thanks_for_nothing.boundary_upstream import BoundaryUpstreamAudit, build_boundary_upstream
from thanks_for_nothing.contracts import LearnedChannel, LearningExperiment, StudyResult
from thanks_for_nothing.emptiness_practice import build_practice_audit
from thanks_for_nothing.gaze import build_gaze_audit
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_joint import GazeUncertainty, build_gaze_uncertainty
from thanks_for_nothing.practice_contracts import ExactDecisionAudit, PracticeAudit
from thanks_for_nothing.practice_exact import build_exact_decision_audit
from thanks_for_nothing.upstream_practice import UpstreamPracticeAudit, build_upstream_practice_audit


@dataclass(frozen=True, slots=True)
class ExperimentalRecords:
    """Already admitted data, without eagerly replaying their numerical producers."""

    practice: PracticeAudit
    upstream_practice: UpstreamPracticeAudit
    exact: ExactDecisionAudit
    gaze: GazeAudit
    parameters: tuple[LearnedChannel, ...]
    uncertainty: GazeUncertainty
    boundary_gaze: BoundaryGazeAudit
    boundary_upstream: BoundaryUpstreamAudit


def read_experimental_records(output: Path) -> ExperimentalRecords:
    """Preserve record admission order before specification, learning and manuscript checks."""
    return ExperimentalRecords(
        read_record(output / "data/emptiness_practice.json", PracticeAudit),
        read_record(output / "data/upstream_practice.json", UpstreamPracticeAudit),
        read_record(output / "data/exact_decision.json", ExactDecisionAudit),
        read_record(output / "data/gaze.json", GazeAudit),
        TypeAdapter(tuple[LearnedChannel, ...]).validate_json(
            (output / "data/learning_parameters.json").read_text()
        ),
        read_record(output / "data/gaze_uncertainty.json", GazeUncertainty),
        read_record(output / "data/boundary_gaze.json", BoundaryGazeAudit),
        read_record(output / "data/boundary_upstream.json", BoundaryUpstreamAudit),
    )


def experimental_replay_gates(
    root: Path,
    study: StudyResult,
    preserved: Path,
    records: ExperimentalRecords,
    learning: LearningExperiment,
) -> tuple[Gate, ...]:
    """Evaluate the five experiment gates at the caller's original replay position."""
    gaze, exact, practice = records.gaze, records.exact, records.practice
    upstream_practice = records.upstream_practice
    return (
        Gate(
            "learned_parameters_replay",
            learning.study == study and learning.parameters == records.parameters,
            "Learned matrices replay before assessment, with shared exposure identities.",
        ),
        Gate(
            "gaze_replication_and_extension_replay",
            gaze.all_controls_pass
            and all(gaze.controls.values())
            and gaze == build_gaze_audit(learning, root=root, specification_dir=preserved),
            "Original percentages, transfer, active scene risk and paired controls replay.",
        ),
        Gate(
            "gaze_joint_uncertainty_replay",
            records.uncertainty.gaze_sha256 == sha256(record_json(gaze).encode()).hexdigest()
            and records.uncertainty.design == gaze.design.joint
            and records.uncertainty.all_controls_pass
            and all(records.uncertainty.controls.values())
            and records.uncertainty == build_gaze_uncertainty(gaze),
            "One paired-block family, exact identities, unavailable constants and coverage replay.",
        ),
        Gate(
            "boundary_gaze_intersection_replay",
            gaze.all_controls_pass
            and all(gaze.controls.values())
            and records.boundary_gaze.all_controls_pass
            and all(records.boundary_gaze.controls.values())
            and records.boundary_gaze == build_boundary_gaze(preserved),
            "Joint scene/encoding sampling, exact nulls, anchored target and 84-member family replay.",
        ),
        Gate(
            "boundary_upstream_integration_replay",
            records.boundary_upstream.all_controls_pass
            and all(records.boundary_upstream.controls.values())
            and records.boundary_upstream == build_boundary_upstream(),
            "Pinned QRF equality, normalized alternative and full-covariance controls replay.",
        ),
        Gate(
            "exact_decision_replay",
            exact.all_controls_pass
            and all(exact.controls.values())
            and exact == build_exact_decision_audit(specification_dir=preserved),
            "Every count, rational selection probability and conditional predictive loss replays.",
        ),
        Gate(
            "emptiness_practice_replay",
            practice.all_controls_pass
            and all(practice.controls.values())
            and practice == build_practice_audit(specification_dir=preserved),
            "Preference/access controls, independent assessment and replicate estimates replay.",
        ),
        Gate(
            "upstream_practice_integration",
            upstream_practice.all_controls_pass and upstream_practice == build_upstream_practice_audit(),
            "Real installed APIs, executing source hashes and bounded upstream controls replay.",
        ),
    )
