# Copyright (c) 2026 Daniel Ari Friedman
"""Session-scoped admitted pipeline for artifact-boundary tests."""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest

from thanks_for_nothing.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class PipelineCase:
    root: Path
    output: Path
    specifications: Path


@pytest.fixture(scope="session")
def pipeline_case(tmp_path_factory):
    root = tmp_path_factory.mktemp("pipeline-source")
    shutil.copytree(ROOT / "data", root / "data")
    shutil.copytree(ROOT / "docs", root / "docs")
    for directory in ("src", "scripts", "notebooks", "typings", "configs", ".github"):
        shutil.copytree(ROOT / directory, root / directory)
    for filename in (
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "AGENTS.md",
        "CONTEXT.md",
        "DESIGN.md",
        "CITATION.cff",
        "LICENSE",
        "LICENSE-PAPER.md",
        "THIRD_PARTY.md",
        "CHANGELOG.md",
    ):
        shutil.copyfile(ROOT / filename, root / filename)
    specifications = root / "models"
    shutil.copytree(ROOT / "src/thanks_for_nothing/models", specifications)
    path = specifications / "gratitude.gnn.md"
    source = path.read_text()
    line = next(line for line in source.splitlines() if line.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"].update(
        replicates=2,
        luckiness=[0.5],
        baseline_days=2,
        intervention_days=2,
        steps_per_day=4,
        assessment_trials=10,
        evaluation_trials=8,
        bootstrap_draws=31,
        permutation_draws=31,
        sensitivity_replicates=2,
        sensitivity_prior_concentrations=[8.0],
        sensitivity_recall_precisions=[4.0],
        calibration_replicates=8,
        calibration_sample_size=32,
        calibration_bootstrap_draws=31,
        calibration_permutation_draws=31,
    )
    path.write_text(source.replace(line, "settings=" + json.dumps(settings)))
    path = specifications / "gaze.gnn.md"
    source = path.read_text()
    line = next(line for line in source.splitlines() if line.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"].update(
        replicates=4,
        steps=8,
        trajectory_steps=4,
        example_strata=[0.5],
        bootstrap_draws=31,
    )
    settings[0]["parameters"]["joint"].update(
        draws=63,
        calibration_experiments=4,
        calibration_units=16,
        calibration_draws=31,
    )
    path.write_text(source.replace(line, "settings=" + json.dumps(settings)))
    path = specifications / "boundary_gaze.gnn.md"
    source = path.read_text()
    line = next(line for line in source.splitlines() if line.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"].update(replicates=4, steps=6, prefixes=[2, 4])
    path.write_text(source.replace(line, "settings=" + json.dumps(settings)))
    path = specifications / "emptiness_practice.gnn.md"
    source = path.read_text()
    line = next(line for line in source.splitlines() if line.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"].update(replicates=4, assessment_samples=8, bootstrap_draws=31)
    path.write_text(source.replace(line, "settings=" + json.dumps(settings)))
    output = root / "output"
    report = run_pipeline(root, output, render=False, notebook=False, specification_dir=specifications)
    assert report.all_pass
    return PipelineCase(root, output, specifications)
