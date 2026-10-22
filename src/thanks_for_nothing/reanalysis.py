# Copyright (c) 2026 Daniel Ari Friedman
"""Replay statistical inference from retained simulation records without new observations."""

from dataclasses import replace
from pathlib import Path

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.calibration import build_calibration_audit
from thanks_for_nothing.emptiness_practice import practice_contrasts
from thanks_for_nothing.gaze_design import load_gaze_task
from thanks_for_nothing.gaze_joint import build_gaze_uncertainty
from thanks_for_nothing.gaze_statistics import active_contrasts, transfer_contrasts
from thanks_for_nothing.statistics import build_statistical_report


def reanalyze(bundle: ResearchBundle, specification_dir: Path) -> ResearchBundle:
    """Recompute derived inference and calibration; preserve all retained simulation rows.

    Source continuity and final artifact qualification remain the caller's
    responsibility. This operation does not certify a changed data generator.
    """
    analysis = load_analysis(specification_dir)
    design = bundle.study.design
    task = load_gaze_task(specification_dir)
    gaze = replace(
        bundle.gaze,
        contrasts=(
            *transfer_contrasts(bundle.gaze.transfer, task),
            *active_contrasts(bundle.gaze.episodes, task),
        ),
    )
    return replace(
        bundle,
        statistics=build_statistical_report(
            bundle.study.rows,
            seed=design.seed + analysis.statistics_seed_offset,
            bootstrap_draws=design.bootstrap_draws,
            permutation_draws=design.permutation_draws,
            analysis=analysis,
        ),
        calibration=build_calibration_audit(design, analysis=analysis),
        practice=replace(
            bundle.practice,
            contrasts=practice_contrasts(bundle.practice.rows, bundle.practice.design, analysis),
        ),
        gaze=gaze,
        gaze_uncertainty=build_gaze_uncertainty(gaze),
    )
