# Copyright (c) 2026 Daniel Ari Friedman
"""Real packaged model copies and source edits used by scientific tests."""

import json
import shutil
from importlib.resources import files
from pathlib import Path


def copy_models(tmp_path):
    root = Path(str(files("thanks_for_nothing").joinpath("models")))
    for file in root.glob("*.gnn.md"):
        (tmp_path / file.name).write_text(file.read_text())
    return tmp_path


def change_gaze_settings(directory, changes):
    path = directory / "gaze.gnn.md"
    text = path.read_text()
    original = next(line for line in text.splitlines() if line.startswith("settings="))
    settings = json.loads(original.removeprefix("settings="))
    settings[0]["parameters"].update(changes)
    path.write_text(text.replace(original, "settings=" + json.dumps(settings, separators=(",", ":"))))


def edit_settings(directory, **parameters):
    edit_model(directory, "emptiness_practice", **parameters)


def edit_model(directory, name, **changes):
    path = directory / f"{name}.gnn.md"
    text = path.read_text()
    line = next(line for line in text.splitlines() if line.startswith("settings="))
    values = json.loads(line[9:])
    values[0]["parameters"].update(changes)
    path.write_text(text.replace(line, "settings=" + json.dumps(values)))


def small_model_directory(root: Path) -> Path:
    source = Path(str(files("thanks_for_nothing").joinpath("models")))
    target = root / "models"
    shutil.copytree(source, target)
    path = target / "gratitude.gnn.md"
    original = path.read_text()
    line = next(line for line in original.splitlines() if line.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"].update(
        seed=9173,
        replicates=3,
        baseline_days=2,
        intervention_days=2,
        steps_per_day=3,
        assessment_trials=8,
        evaluation_trials=16,
        bootstrap_draws=63,
        permutation_draws=63,
        calibration_replicates=4,
        calibration_sample_size=16,
        calibration_bootstrap_draws=63,
        calibration_permutation_draws=63,
        sensitivity_replicates=2,
        sensitivity_prior_concentrations=[2.0, 8.0, 16.0],
        sensitivity_recall_precisions=[1.0, 2.0, 4.0],
    )
    path.write_text(original.replace(line, "settings=" + json.dumps(settings)))
    for name in ("attention_positive", "attention_negative"):
        path = target / f"{name}.gnn.md"
        original = path.read_text()
        line = next(line for line in original.splitlines() if line.startswith("settings="))
        settings = json.loads(line.removeprefix("settings="))
        settings[0]["parameters"]["num_timesteps"] = 3
        path.write_text(original.replace(line, "settings=" + json.dumps(settings)))
    return target
