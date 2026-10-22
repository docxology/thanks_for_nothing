# Copyright (c) 2026 Daniel Ari Friedman
"""Numerical research generation, independent of publication and artifact serialization."""

from dataclasses import dataclass
from pathlib import Path

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.attention import build_attention_audit
from thanks_for_nothing.boundary_study import build_boundary_gaze
from thanks_for_nothing.boundary_upstream import build_boundary_upstream
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.calibration import build_calibration_audit
from thanks_for_nothing.contracts import LearnedChannel
from thanks_for_nothing.emptiness_practice import build_practice_audit
from thanks_for_nothing.experiments import run_learning_experiment
from thanks_for_nothing.gaze import build_gaze_audit
from thanks_for_nothing.gaze_joint import build_gaze_uncertainty
from thanks_for_nothing.nothingness import build_nothingness_audit
from thanks_for_nothing.practice_exact import build_exact_decision_audit
from thanks_for_nothing.provenance import build_provenance_audit
from thanks_for_nothing.sensitivity import build_sensitivity_audit
from thanks_for_nothing.source_reconstruction import (
    SourceReconstruction,
    build_source_audit,
    run_source_reconstruction,
)
from thanks_for_nothing.statistics import build_statistical_report
from thanks_for_nothing.upstream_practice import build_upstream_practice_audit


@dataclass(frozen=True, slots=True)
class ResearchRun:
    """Keep retained numerical arrays separate from serialized records and local publication."""

    bundle: ResearchBundle
    parameters: tuple[LearnedChannel, ...]
    reconstruction: SourceReconstruction


def generate_research(root: Path, specifications: Path, *, replicates: int | None = None) -> ResearchRun:
    """Execute admitted scientific stages without writing products or certifying a release."""
    analysis = load_analysis(specifications)
    provenance = build_provenance_audit(root)
    source = build_source_audit(root, analysis=analysis)
    source_run = run_source_reconstruction(root=root, analysis=analysis)
    learning = run_learning_experiment(replicates=replicates, specification_dir=specifications)
    study = learning.study
    statistics = build_statistical_report(
        study.rows,
        seed=study.design.seed + analysis.statistics_seed_offset,
        bootstrap_draws=study.design.bootstrap_draws,
        permutation_draws=study.design.permutation_draws,
        analysis=analysis,
    )
    absence = build_nothingness_audit(specification_dir=specifications)
    attention = build_attention_audit(
        specification_dir=specifications, output_dir=specifications.parent / "gnn/execution"
    )
    calibration = build_calibration_audit(study.design, analysis=analysis)
    sensitivity = build_sensitivity_audit(study.design, specification_dir=specifications)
    practice = build_practice_audit(specification_dir=specifications)
    upstream_practice = build_upstream_practice_audit()
    exact = build_exact_decision_audit(specification_dir=specifications)
    gaze = build_gaze_audit(learning, root=root, specification_dir=specifications)
    uncertainty = build_gaze_uncertainty(gaze)
    boundary_gaze = build_boundary_gaze(specifications)
    boundary_upstream = build_boundary_upstream()
    bundle = ResearchBundle(
        provenance,
        source,
        study,
        statistics,
        absence,
        attention,
        calibration,
        sensitivity,
        practice,
        upstream_practice,
        exact,
        gaze,
        uncertainty,
        boundary_gaze,
        boundary_upstream,
    )
    return ResearchRun(bundle, learning.parameters, source_run)
