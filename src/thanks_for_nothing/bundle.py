# Copyright (c) 2026 Daniel Ari Friedman
"""Typed aggregate of separately qualified research layers."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from thanks_for_nothing.attention import AttentionAudit
from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.boundary_upstream import BoundaryUpstreamAudit
from thanks_for_nothing.calibration import CalibrationAudit
from thanks_for_nothing.contracts import StudyResult
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_joint import GazeUncertainty
from thanks_for_nothing.nothingness import NothingnessAudit
from thanks_for_nothing.practice_contracts import ExactDecisionAudit, PracticeAudit
from thanks_for_nothing.provenance import ProvenanceAudit
from thanks_for_nothing.sensitivity import SensitivityAudit
from thanks_for_nothing.source_reconstruction import SourceAudit
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.upstream_practice import UpstreamPracticeAudit


@dataclass(frozen=True, slots=True)
class ResearchBundle:
    """Retain provenance, reconstruction and new model evidence as distinct records."""

    provenance: ProvenanceAudit
    source: SourceAudit
    study: StudyResult
    statistics: StatisticalReport
    nothingness: NothingnessAudit
    attention: AttentionAudit
    calibration: CalibrationAudit
    sensitivity: SensitivityAudit
    practice: PracticeAudit
    upstream_practice: UpstreamPracticeAudit
    exact_decision: ExactDecisionAudit
    gaze: GazeAudit
    gaze_uncertainty: GazeUncertainty
    boundary_gaze: BoundaryGazeAudit
    boundary_upstream: BoundaryUpstreamAudit


def read_bundle(output: Path) -> ResearchBundle:
    """Read and type-admit the complete artifact bundle for deterministic publication replay."""
    names = {
        "provenance": "provenance",
        "source": "source_audit",
        "study": "study",
        "statistics": "statistics",
        "nothingness": "nothingness",
        "attention": "attention",
        "calibration": "statistical_calibration",
        "sensitivity": "sensitivity",
        "practice": "emptiness_practice",
        "upstream_practice": "upstream_practice",
        "exact_decision": "exact_decision",
        "gaze": "gaze",
        "gaze_uncertainty": "gaze_uncertainty",
        "boundary_gaze": "boundary_gaze",
        "boundary_upstream": "boundary_upstream",
    }
    payload = {
        field: TypeAdapter(JsonValue).validate_json((output / "data" / f"{name}.json").read_text())
        for field, name in names.items()
    }
    return TypeAdapter(ResearchBundle).validate_python(payload)
