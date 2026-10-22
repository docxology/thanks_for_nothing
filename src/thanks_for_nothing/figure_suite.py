# Copyright (c) 2026 Daniel Ari Friedman
"""One source-bound figure suite shared by numerical production and publication previews."""

from pathlib import Path

from thanks_for_nothing.artifact_checks import read_record
from thanks_for_nothing.boundary_figures import (
    boundary_allocation,
    boundary_convergence,
    boundary_information,
    boundary_outcomes,
    boundary_structure,
)
from thanks_for_nothing.boundary_paths import boundary_paths
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.concept_figures import concept_operations
from thanks_for_nothing.experiment_overview import experiment_overview
from thanks_for_nothing.figures import generate_figures
from thanks_for_nothing.gaze_figures import (
    gaze_inquiry_paths,
    gaze_transfer_paths,
    yarbus_reconstruction,
)
from thanks_for_nothing.gaze_situations import boundary_situation, gaze_situation
from thanks_for_nothing.gaze_summary_figures import gaze_inquiry_summary, gaze_transfer_summary
from thanks_for_nothing.gnn_figures import gnn_model_graph, gnn_model_tensors
from thanks_for_nothing.joint_figures import joint_coverage, joint_gaze_summary
from thanks_for_nothing.learning_situations import practice_situation, recall_situation
from thanks_for_nothing.practice_figures import exact_decision, practice_policies, practice_revision
from thanks_for_nothing.practice_mechanism import practice_mechanism
from thanks_for_nothing.sampling_diagnostics import SamplingAudit
from thanks_for_nothing.sampling_figures import sampling_precision
from thanks_for_nothing.task_figures import boundary_task, task_settings
from thanks_for_nothing.tradition_figures import world_traditions
from thanks_for_nothing.visual_style import FigureRecord


def generate_all_figures(bundle: ResearchBundle, output: Path) -> tuple[FigureRecord, ...]:
    """Draw every scientific view from the same admitted bundle and preserve its numerical sources."""
    return (
        gnn_model_graph(output),
        gnn_model_tensors(output),
        world_traditions(output),
        *generate_figures(
            bundle.study,
            bundle.statistics,
            bundle.nothingness,
            bundle.attention,
            bundle.sensitivity,
            bundle.calibration,
            output,
        ),
        practice_policies(bundle.practice, output),
        practice_revision(bundle.practice, output),
        practice_mechanism(bundle.practice, output),
        exact_decision(bundle.exact_decision, output),
        yarbus_reconstruction(bundle.gaze, output),
        gaze_transfer_paths(bundle.gaze, output),
        gaze_transfer_summary(bundle.gaze, output),
        gaze_inquiry_paths(bundle.gaze, output),
        gaze_inquiry_summary(bundle.gaze, output),
        joint_gaze_summary(bundle.gaze, bundle.gaze_uncertainty, output),
        joint_coverage(bundle.gaze_uncertainty, output),
        boundary_information(bundle.boundary_gaze, output),
        boundary_outcomes(bundle.boundary_gaze, output),
        boundary_allocation(bundle.boundary_gaze, output),
        boundary_convergence(bundle.boundary_gaze, output),
        boundary_structure(bundle.boundary_upstream, output),
        boundary_paths(bundle.boundary_gaze, bundle.gaze.design, output),
        task_settings(bundle, output),
        experiment_overview(bundle, output),
        boundary_task(bundle, output),
        concept_operations(bundle, output),
        recall_situation(bundle.study, bundle.statistics, output),
        practice_situation(bundle.practice, output),
        gaze_situation(bundle.gaze, bundle.gaze_uncertainty, output),
        boundary_situation(bundle.boundary_gaze, output),
        sampling_precision(
            read_record(output.parent / "data/sampling_diagnostics.json", SamplingAudit), output
        ),
    )
