# Copyright (c) 2026 Daniel Ari Friedman
import json

import numpy as np
import pytest

from tests.support.models import change_gaze_settings, copy_models, edit_model
from thanks_for_nothing.boundary_design import load_boundary_task
from thanks_for_nothing.boundary_math import boundary_policy, query_costs
from thanks_for_nothing.boundary_sampling import make_exposure, run_boundary_episode
from thanks_for_nothing.boundary_study import boundary_mathematical_controls
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_active import GazeExposure, gaze_policy, run_gaze_episode
from thanks_for_nothing.gaze_design import load_gaze_task


def test_declared_scene_and_probe_counts_drive_execution(tmp_path):
    copy_models(tmp_path)
    original = load_gaze_task(tmp_path)
    change_gaze_settings(
        tmp_path,
        {
            "coordinates": list(original.design.coordinates[:4]),
            "regions": [0, 1, 2, 0],
            "transfer_state_map": [list(row[:4]) for row in original.design.transfer_state_map],
            "initial_location": 0,
        },
    )
    edit_model(tmp_path, "boundary_gaze", probe_reliabilities=[0.6, 0.8], probe_costs=[0.01, 0.04])
    task = load_boundary_task(tmp_path)
    assert len(task.diagnostic) == len(task.gaze.design.coordinates) + len(task.design.probe_costs) == 6
    policy = boundary_policy(task, task.open_prior, 0, "diagnostic", "integrated")
    assert policy.shape == (6,)
    assert sum(policy) == pytest.approx(1)
    assert np.asarray(query_costs(task, 0)).shape == (6,)
    exposure = make_exposure(task, "diagnostic", 0, 0, 0)
    row = run_boundary_episode(task, exposure, "integrated")
    assert max(row.queries) < 6
    assert len(row.queries) == task.design.steps
    assert all(boundary_mathematical_controls(task).values())
    gaze_exposure = GazeExposure(
        "example",
        0,
        0,
        0,
        np.full(task.gaze.design.steps, 0.9),
        np.full((task.gaze.design.steps, 3), 0.5),
        "synthetic-control",
    )
    gaze_row = run_gaze_episode(task.gaze, gaze_exposure, "uniform_open")
    assert set(gaze_row.locations) == {3}


@pytest.mark.parametrize(
    "changes",
    [
        {"regions": [0] * 13},
        {"regions": [0, 1, 2]},
        {"initial_location": 13},
        {"trajectory_steps": 10000},
        {"coordinates": [[0, 0]] * 12},
        {"coordinates": [[-1, 0]] * 13},
        {"contexts": [{"name": "x", "candidates": [3]}]},
        {"conditions": ["sham", "sham"]},
        {"conditions": ["inquiry_open", "uniform_open"]},
        {"contexts": [{"name": "x", "candidates": [0]}, {"name": "x", "candidates": [0]}]},
        {"channels": [[[0.5, 0.5, 0.5]] * 3] * 3},
        {"channels": [[[0.4, 0.4, 0.4], [0.3, 0.3, 0.3], [0.3, 0.3, 0.3]]] * 3},
    ],
)
def test_real_invalid_gnn_changes_rejected(tmp_path, changes):
    copy_models(tmp_path)
    change_gaze_settings(tmp_path, changes)
    with pytest.raises((ContractError, ValueError)):
        load_gaze_task(tmp_path)


def test_real_preferences_and_policy_weight_change_numbers(tmp_path):
    copy_models(tmp_path)
    first = load_gaze_task(tmp_path)
    policy, _, _ = gaze_policy(first, first.open_prior, first.design.initial_location)
    path = tmp_path / "gaze.gnn.md"
    path.write_text(path.read_text().replace("C=[2.0,0.0,-2.0]", "C=[-2.0,0.0,2.0]"))
    second = load_gaze_task(tmp_path)
    changed, _, _ = gaze_policy(second, second.open_prior, second.design.initial_location)
    assert first.model.source_hash != second.model.source_hash
    assert max(abs(policy - changed)) > 0.05
    change_gaze_settings(tmp_path, {"information_weight": 0})
    third = load_gaze_task(tmp_path)
    ablated, _, _ = gaze_policy(third, third.open_prior, third.design.initial_location)
    assert max(abs(changed - ablated)) > 0.001


def test_real_structural_admission_is_consumed(tmp_path):
    copy_models(tmp_path)
    first = load_gaze_task(tmp_path)
    path = tmp_path / "emptiness_practice.gnn.md"
    text = path.read_text()
    original = next(line for line in text.splitlines() if line.startswith("settings="))
    settings = json.loads(original.removeprefix("settings="))
    settings[0]["parameters"]["deployments"][2]["labels"] = ["self", "env", "env"]
    path.write_text(text.replace(original, "settings=" + json.dumps(settings, separators=(",", ":"))))
    with pytest.raises(ContractError, match="proper restricted subset"):
        load_gaze_task(tmp_path)
    assert first.restricted_prior[2] == 0
