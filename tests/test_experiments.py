# Copyright (c) 2026 Daniel Ari Friedman
"""Paired study tests use independent RNG streams and physical GNN files."""

import json
from dataclasses import asdict

import numpy as np
import pytest
from pydantic import ValidationError

from tests.support.models import copy_models
from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.experiments import run_study, sample_world, train_day
from thanks_for_nothing.inference import optimism
from thanks_for_nothing.specifications import load_study


def test_exact_replay_and_semantic_nulls():
    first = run_study(replicates=2, seed=83)
    assert first == run_study(replicates=2, seed=83)
    assert first != run_study(replicates=2, seed=84)
    assert all(first.controls.values())
    assert len(first.rows) == 40
    assert len(first.traces) == len(first.rows) * (
        first.design.baseline_days + first.design.intervention_days
    )
    assert json.loads(json.dumps(asdict(first)))["design"]["replicates"] == 2
    assert any(row.appreciation > 0 for row in first.rows)
    assert all(0 <= row.brier_post <= 1 for row in first.rows)
    for i in range(0, len(first.rows), 4):
        group = first.rows[i : i + 4]
        assert group[0].brier_post == group[3].brier_post
        assert group[1].mean_recall_count == group[2].mean_recall_count
        assert group[0].mean_recall_count == 0
    assert any(first.rows[i].brier_post != first.rows[i + 1].brier_post for i in range(0, 40, 4))


def test_zero_positive_day_has_zero_recall():
    model, design = load_study()
    counts = np.asarray(model.tensors.A) * design.prior_concentration
    for condition in (Condition.POSITIVE, Condition.RANDOM):
        day = train_day(
            counts,
            np.ones(12, dtype=int),
            np.array([0.5, 0.5]),
            np.full((2, 2), 0.5),
            design,
            condition,
            np.random.default_rng(4),
        )
        assert day.recalled == 0


def test_world_sampler_extremes():
    likelihood = np.array([[1.0, 0.0], [0.0, 1.0]])
    states, obs = sample_world(np.random.default_rng(3), 1, likelihood, 10)
    np.testing.assert_array_equal(states, obs)
    assert states.sum() == 0


def test_gnn_a_b_changes_reach_actual_study(tmp_path):
    copy_models(tmp_path)
    baseline = run_study(replicates=1, seed=42, specification_dir=tmp_path)
    path = tmp_path / "gratitude.gnn.md"
    original = path.read_text()
    path.write_text(
        original.replace("A=[[0.7,0.2],[0.1,0.1],[0.2,0.7]]", "A=[[0.6,0.3],[0.1,0.1],[0.3,0.6]]")
    )
    changed = run_study(replicates=1, seed=42, specification_dir=tmp_path)
    assert changed.rows[0].brier_post != baseline.rows[0].brier_post
    path.write_text(
        original.replace("B=[[[0.5],[0.5]],[[0.5],[0.5]]]", "B=[[[0.8],[0.8]],[[0.2],[0.2]]]")
    )
    assert (
        run_study(replicates=1, seed=42, specification_dir=tmp_path).rows[0].brier_post
        != baseline.rows[0].brier_post
    )
    path.write_text(original.replace('"reference_hazard":0.3', '"reference_hazard":0.0'))
    null = run_study(replicates=1, seed=42, specification_dir=tmp_path)
    assert all(r.appreciation == 0 for r in null.rows)
    assert null.rows[0].brier_post == baseline.rows[0].brier_post


@pytest.mark.parametrize("kwargs", [{"replicates": 0}, {"replicates": True}, {"seed": -1}])
def test_invalid_overrides(kwargs):
    with pytest.raises(ValidationError):
        run_study(**kwargs)


def test_declared_prior_changes_actual_beliefs(tmp_path):
    copy_models(tmp_path)
    before = run_study(replicates=1, seed=42, specification_dir=tmp_path)
    path = tmp_path / "gratitude.gnn.md"
    path.write_text(path.read_text().replace("D=[0.5,0.5]", "D=[0.8,0.2]"))
    after = run_study(replicates=1, seed=42, specification_dir=tmp_path)
    assert before.rows[0].post_world_well != after.rows[0].post_world_well
    assert before.rows[0].exposure_sha256 == after.rows[0].exposure_sha256


def test_well_mode_has_intended_readout_orientation():

    _, design = load_study()
    priors = np.array([0.2, 0.5, 0.8])
    assert optimism(1, priors, np.asarray(design.optimism_well), np.asarray(design.optimism_poor)) > 0
    assert optimism(0, priors, np.asarray(design.optimism_well), np.asarray(design.optimism_poor)) < 0
