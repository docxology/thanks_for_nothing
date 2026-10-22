# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace

import numpy as np
import pytest
from pydantic import ValidationError

from tests.support.models import edit_model
from thanks_for_nothing.boundary_design import contingency_channel, load_boundary_task
from thanks_for_nothing.boundary_math import boundary_policy, joint_prediction, population_regret
from thanks_for_nothing.boundary_sampling import make_exposure, run_boundary_episode
from thanks_for_nothing.boundary_statistics import boundary_estimates
from thanks_for_nothing.boundary_study import boundary_mathematical_controls, build_boundary_gaze
from thanks_for_nothing.contracts import ContractError


def test_imported_admission_and_all_controls(boundary_models):
    task = load_boundary_task(boundary_models)
    assert task.diagnostic.shape == task.label_only.shape == (16, 9, 9)
    assert task.restricted_prior.reshape(3, 3).tolist() == [[1 / 6, 1 / 6, 0]] * 3
    assert all(boundary_mathematical_controls(task).values())
    assert task.channels("label_only") is task.label_only
    assert population_regret(task, np.array([0.0, 1.0, 0.0]), 1) == 0
    with pytest.raises(ContractError, match="not declared"):
        task.channels("forged")
    with pytest.raises(ContractError, match="normalized scene"):
        population_regret(task, np.array([0.0, 0.0, 0.0]), 1)
    with pytest.raises(ContractError, match="normalized scene"):
        population_regret(task, np.array([0.0, 1.0, 0.0]), 3)


def test_joint_information_independent_known_answer():
    channel = np.array([[[0.45, 0.05], [0.05, 0.45], [0.05, 0.45], [0.45, 0.05]]])
    prediction, information = joint_prediction(channel, np.array([0.5, 0.5]))
    assert prediction.tolist() == [[0.25] * 4]
    assert information[0] == pytest.approx(0.3680642071684971)
    assert channel.reshape(2, 2, 2).sum(axis=0).tolist() == [[0.5, 0.5]] * 2
    assert channel.reshape(2, 2, 2).sum(axis=1).tolist() == [[0.5, 0.5]] * 2
    for reliability in (0.65, 0.8, 0.95):
        probe = contingency_channel(reliability)
        _, info = joint_prediction(probe[None, :, :], np.full(3, 1 / 3))
        oracle = (
            np.log(3)
            + reliability * np.log(reliability)
            + (1 - reliability) * np.log((1 - reliability) / 2)
        )
        assert info[0] == pytest.approx(oracle)


@pytest.mark.parametrize("reliability", [1 / 3, 0, 1, float("nan")])
def test_invalid_contingency_rejected(reliability):
    with pytest.raises(ContractError, match="reliability"):
        contingency_channel(reliability)


@pytest.mark.parametrize(
    "posterior",
    [np.array([1.0]), np.array([0.0, 0.0]), np.array([-1.0, 2.0]), np.array([float("nan"), 0.0])],
)
def test_invalid_joint_prediction_rejected(posterior):
    with pytest.raises(ContractError, match="normalized channels"):
        joint_prediction(np.full((1, 2, 2), 0.5), posterior)


def test_paired_runtime_replay_and_independent_product_oracle(small_boundary):
    directory, audit = small_boundary
    assert audit == build_boundary_gaze(directory)
    assert audit.all_controls_pass
    assert len(audit.episodes) == 2 * 3 * 3 * 4 * 6
    assert len(audit.region.intervals) == 84
    assert len(audit.exact_offsets) == 30
    assert len(audit.convergence) == 168
    task = load_boundary_task(directory)
    indexed = {(r.regime, r.scene, r.boundary, r.replicate, r.condition): r for r in audit.episodes}
    for row in audit.episodes:
        expected = (
            task.restricted_prior.copy() if row.condition == "restricted" else task.open_prior.copy()
        )
        for query, outcome in zip(row.queries, row.outcomes, strict=True):
            channel = task.channels(row.regime)[query]
            likelihood = channel[outcome]
            if row.condition == "sham" and query >= 13:
                likelihood = channel.reshape(3, 3, 9).sum(axis=0)[outcome % 3]
            expected *= likelihood
        expected /= expected.sum()
        assert row.final_joint == pytest.approx(expected, abs=1e-12)
        if row.condition == "sham":
            paired = indexed[row.regime, row.scene, row.boundary, row.replicate, "integrated"]
            assert (row.queries, row.outcomes, row.mean_cost) == (
                paired.queries,
                paired.outcomes,
                paired.mean_cost,
            )
        if row.condition == "boundary_only":
            assert row.final_scene == pytest.approx([1 / 3] * 3)
        if row.regime == "label_only" or row.condition in ("visual", "sham"):
            prior = task.gaze.restricted_prior if row.condition == "restricted" else task.gaze.open_prior
            assert row.final_boundary == pytest.approx(prior)
    offsets = dict(audit.exact_offsets)
    assert offsets["label_only/H2/restricted/visual/boundary_brier"] == pytest.approx(5 / 6)
    assert offsets["label_only/H0/restricted/visual/boundary_brier"] == pytest.approx(-1 / 6)


def test_increased_n_preserves_unit_seed_and_episode(boundary_models):
    task = load_boundary_task(boundary_models)
    before = make_exposure(task, "diagnostic", 2, 1, 3)
    episode = run_boundary_episode(task, before, "integrated")
    edit_model(boundary_models, "boundary_gaze", replicates=8, prefixes=[2, 4, 8])
    larger = load_boundary_task(boundary_models)
    after = make_exposure(larger, "diagnostic", 2, 1, 3)
    assert before.sha256 == after.sha256
    assert np.array_equal(before.outcomes, after.outcomes)
    assert episode == run_boundary_episode(larger, after, "integrated")
    assert after.sha256 != make_exposure(larger, "diagnostic", 2, 1, 4).sha256


@pytest.mark.parametrize(
    "changes",
    [
        {"replicates": 1},
        {"prefixes": [2, 3]},
        {"prefixes": [4, 2]},
        {"probe_costs": [0.1]},
        {"probe_costs": [-1, 0, 0]},
        {"probe_reliabilities": [0.3, 0.8, 0.9]},
        {"conditions": ["visual", "integrated"]},
        {"regimes": ["diagnostic"]},
        {"endpoints": ["boundary_brier"]},
        {"scene_maps": [[0, 0, 0]] * 3},
    ],
)
def test_invalid_real_gnn_edits_rejected(boundary_models, changes):
    edit_model(boundary_models, "boundary_gaze", **changes)
    with pytest.raises((ContractError, ValidationError)):
        load_boundary_task(boundary_models)


@pytest.mark.parametrize("line", ["C=[1,0,0,0,0,0,0,0,0]", "D=[1,0,0,0,0,0,0,0,0]"])
def test_noncanonical_actual_tensor_rejected(boundary_models, line):
    path = boundary_models / "boundary_gaze.gnn.md"
    source = path.read_text()
    prefix = line[:2]
    old = next(value for value in source.splitlines() if value.startswith(prefix))
    path.write_text(source.replace(old, line))
    with pytest.raises(ContractError, match="canonical tensors"):
        load_boundary_task(boundary_models)


@pytest.mark.parametrize(
    "kind", ["missing", "duplicate", "hash", "posterior", "brier", "schedule", "support"]
)
def test_statistical_admission_fails_for_broken_records(small_boundary, kind):
    directory, audit = small_boundary
    rows = audit.episodes
    if kind == "missing":
        rows = rows[:-1]
    elif kind == "duplicate":
        rows = (*rows, rows[0])
    else:
        index = next(i for i, row in enumerate(rows) if row.condition == "sham")
        row = rows[index]
        changes = {
            "hash": {"exposure_sha256": "wrong"},
            "posterior": {"final_joint": (1.0,)},
            "brier": {"boundary_brier": 0.1},
            "schedule": {"queries": (15,) * 6},
            "support": {"final_boundary": (0.0, 0.0, 1.0)},
        }[kind]
        rows = (*rows[:index], replace(row, **changes), *rows[index + 1 :])
    with pytest.raises(ContractError):
        boundary_estimates(load_boundary_task(directory), rows)


def test_invalid_exposure_and_policy_rejected(boundary_models):
    task = load_boundary_task(boundary_models)
    exposure = make_exposure(task, "diagnostic", 0, 0, 0)
    for changes in ({"scene": 3}, {"replicate": 5}, {"actions": np.ones(6)}, {"sha256": "wrong"}):
        with pytest.raises(ContractError, match="paired uniforms"):
            run_boundary_episode(task, replace(exposure, **changes), "integrated")
    with pytest.raises(ContractError, match="valid sham schedule"):
        run_boundary_episode(task, exposure, "sham")
    with pytest.raises(ContractError, match="valid sham schedule"):
        run_boundary_episode(task, exposure, "sham", yoked_queries=(99,) * 6)
    with pytest.raises(ContractError, match="outside the declared"):
        make_exposure(task, "diagnostic", 3, 0, 0)
    for condition, location in (("sham", 10), ("visual", 13)):
        with pytest.raises(ContractError, match="autonomous boundary policy"):
            boundary_policy(task, task.open_prior, location, "diagnostic", condition)
