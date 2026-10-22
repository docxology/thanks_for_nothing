# Copyright (c) 2026 Daniel Ari Friedman
"""Typed artifact persistence shared by research orchestration and saved-record workflows."""

import csv
import shutil
from importlib.resources import files
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np

from thanks_for_nothing.analysis_design import AnalysisDesign
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.concepts import CONCEPTS
from thanks_for_nothing.contracts import StudyResult
from thanks_for_nothing.sampling_diagnostics import build_sampling_audit
from thanks_for_nothing.source_reconstruction import SourceReconstruction
from thanks_for_nothing.specifications import load_model


def preserve_specifications(source: Path | None, destination: Path) -> None:
    """Admit the complete selected GNN source set before updating any preserved models."""
    packaged = files("thanks_for_nothing").joinpath("models")
    chosen = Path(str(packaged)) if source is None else source
    required = sorted(entry.name for entry in packaged.iterdir() if entry.name.endswith(".gnn.md"))
    for name in required:
        _ = load_model(name.removesuffix(".gnn.md"), chosen)
    _ = shutil.copytree(chosen, destination, dirs_exist_ok=True)


def write_agent_csv(path: Path, study: StudyResult) -> None:
    """Write one explicit row per agent-condition pair with exposure identity."""
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            (
                "condition",
                "luckiness",
                "replicate",
                "paired_id",
                "pre_world_well",
                "post_world_well",
                "brier_pre",
                "brier_post",
                "nll_pre",
                "nll_post",
                "entropy_post",
                "optimism_pre",
                "optimism_post",
                "appreciation",
                "mean_recall_count",
                "exposure_sha256",
            )
        )
        writer.writerows(
            (
                r.condition,
                r.luckiness,
                r.replicate,
                r.paired_id,
                r.pre_world_well,
                r.post_world_well,
                r.brier_pre,
                r.brier_post,
                r.nll_pre,
                r.nll_post,
                r.entropy_post,
                r.optimism_pre,
                r.optimism_post,
                r.appreciation,
                r.mean_recall_count,
                r.exposure_sha256,
            )
            for r in study.rows
        )


def write_bundle_evidence(data: Path, bundle: ResearchBundle, analysis: AnalysisDesign) -> None:
    """Persist one admitted bundle with its selected analysis declaration."""
    write_record(data / "concepts.json", CONCEPTS)
    write_agent_csv(data / "agents.csv", bundle.study)
    for name, record in (
        ("analysis_protocol", analysis),
        (
            "sampling_diagnostics",
            build_sampling_audit(bundle, analysis),
        ),
        ("provenance", bundle.provenance),
        ("source_audit", bundle.source),
        ("study", bundle.study),
        ("statistics", bundle.statistics),
        ("nothingness", bundle.nothingness),
        ("attention", bundle.attention),
        ("statistical_calibration", bundle.calibration),
        ("sensitivity", bundle.sensitivity),
        ("emptiness_practice", bundle.practice),
        ("upstream_practice", bundle.upstream_practice),
        ("exact_decision", bundle.exact_decision),
        ("gaze", bundle.gaze),
        ("gaze_uncertainty", bundle.gaze_uncertainty),
        ("boundary_gaze", bundle.boundary_gaze),
        ("boundary_upstream", bundle.boundary_upstream),
    ):
        write_record(data / f"{name}.json", record)


def write_source_arrays(path: Path, source_run: SourceReconstruction) -> None:
    """Preserve the named source arrays without requiring a publication build."""
    arrays = {
        "luckiness": source_run.luckiness,
        "baseline": source_run.baseline,
        "intervention": source_run.intervention,
        "baseline_snapshots_before": source_run.baseline_snapshots_before,
        "baseline_snapshots_after": source_run.baseline_snapshots_after,
        "updates_before": source_run.updates_before,
        "updates_after": source_run.updates_after,
    }
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name, values in arrays.items():
            with archive.open(name + ".npy", "w") as stream:
                np.lib.format.write_array(stream, values, allow_pickle=False)
