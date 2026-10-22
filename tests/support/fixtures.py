# Copyright (c) 2026 Daniel Ari Friedman
"""Shared scientific fixtures with their original scopes and budgets."""

import json
import shutil
from pathlib import Path

import pytest

from tests.support.models import change_gaze_settings, copy_models, edit_model, edit_settings
from thanks_for_nothing.boundary_study import build_boundary_gaze
from thanks_for_nothing.experiments import run_learning_experiment
from thanks_for_nothing.gaze import build_gaze_audit
from thanks_for_nothing.gaze_design import load_gaze_task

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def small_gaze(tmp_path_factory):
    directory = tmp_path_factory.mktemp("gaze-models")
    copy_models(directory)
    joint = load_gaze_task().design.joint.model_dump()
    joint.update(draws=127, calibration_experiments=4, calibration_units=16, calibration_draws=63)
    change_gaze_settings(
        directory,
        {"replicates": 4, "steps": 8, "trajectory_steps": 4, "bootstrap_draws": 63, "joint": joint},
    )
    experiment = run_learning_experiment(replicates=3, specification_dir=directory)
    return directory, experiment, build_gaze_audit(experiment, specification_dir=directory)


@pytest.fixture
def practice_models(tmp_path):
    directory = tmp_path / "models"
    shutil.copytree(ROOT / "src/thanks_for_nothing/models", directory)
    edit_settings(directory, replicates=4, bootstrap_draws=63, assessment_samples=16)
    return directory


@pytest.fixture
def boundary_models(tmp_path):
    directory = tmp_path / "models"
    shutil.copytree(ROOT / "src/thanks_for_nothing/models", directory)
    edit_model(directory, "boundary_gaze", replicates=4, steps=6, prefixes=[2, 4])
    gaze = directory / "gaze.gnn.md"
    text = gaze.read_text()
    line = next(line for line in text.splitlines() if line.startswith("settings="))
    values = json.loads(line[9:])
    values[0]["parameters"]["joint"]["draws"] = 63
    gaze.write_text(text.replace(line, "settings=" + json.dumps(values)))
    return directory


@pytest.fixture
def small_boundary(boundary_models):
    return boundary_models, build_boundary_gaze(boundary_models)
