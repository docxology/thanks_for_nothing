# Copyright (c) 2026 Daniel Ari Friedman
"""Real-source numerical controls for the bounded notebook adapter."""

import shutil
from pathlib import Path

import numpy as np
import pytest

from thanks_for_nothing.source_reconstruction import (
    SourceInputError,
    build_source_audit,
    run_source_reconstruction,
    run_yarbus_reconstruction,
    source_posterior,
)

ROOT = Path(__file__).resolve().parents[1]


def test_replay_when_seed_is_identical():
    # Given a small real-source run, when replayed with the same seed.
    first = run_source_reconstruction(42, 3, 2, 4, root=ROOT)
    second = run_source_reconstruction(42, 3, 2, 4, root=ROOT)
    # Then all generated trajectories and task updates are identical.
    np.testing.assert_array_equal(first.baseline, second.baseline)
    np.testing.assert_array_equal(first.intervention, second.intervention)
    np.testing.assert_array_equal(first.updates_after, second.updates_after)
    assert np.isfinite(first.updates_before).all()
    assert np.isfinite(first.intervention).all()


def test_trajectories_when_seed_changes():
    # Given otherwise identical inputs, when the seed changes.
    first = run_source_reconstruction(1, 3, 2, 4, root=ROOT)
    second = run_source_reconstruction(2, 3, 2, 4, root=ROOT)
    # Then generated observations differ.
    assert not np.array_equal(first.baseline[:, :, 1], second.baseline[:, :, 1])


def test_source_snapshot_when_intervention_mutates_view():
    # Given original baseline snapshots, when source intervention executes.
    result = run_source_reconstruction(3, 2, 2, 4, root=ROOT)
    # Then the selected snapshot is mutated, earlier snapshot remains untouched.
    assert result.shares_baseline_memory
    np.testing.assert_array_equal(
        result.baseline_snapshots_before[:, 0], result.baseline_snapshots_after[:, 0]
    )
    assert not np.array_equal(
        result.baseline_snapshots_before[:, -1], result.baseline_snapshots_after[:, -1]
    )
    assert result.baseline_snapshots_before[0, 0].sum() == pytest.approx(2)
    assert result.baseline_snapshots_before[0, 1].sum() == pytest.approx(10)
    assert not np.array_equal(result.task_priors_before, result.task_priors_after)


def test_raw_counts_when_columns_have_unequal_mass():
    # Given equally shaped columns with masses 18 and 2, when source inference runs.
    raw = source_posterior(np.array([0.5, 0.5]), np.array([9.0, 1.0]))
    normalized = source_posterior(np.array([0.5, 0.5]), np.array([0.5, 0.5]))
    # Then the raw mass creates a posterior difference absent after normalization.
    assert raw[0] == pytest.approx(4.50001 / 5.00002)
    assert normalized[0] == 0.5
    assert raw[0] - normalized[0] > 0.39


def test_epsilon_when_state_has_zero_weight():
    # Given a zero-likelihood state, when source smoothing is applied.
    posterior = source_posterior(np.array([0.5, 0.5]), np.array([1.0, 0.0]))
    # Then the retained source epsilon differs from exact Bayes' zero.
    assert posterior[1] == pytest.approx(0.00001 / 0.50002)
    assert posterior[1] > 0


def test_audit_when_source_is_admitted():
    # Given the digest-admitted real file, when numerical audit controls execute.
    audit = build_source_audit(ROOT)
    # Then the endpoint label and actual numeric failure modes are observable.
    assert audit["cell_count"] == 16
    controls = audit["controls"]
    assert controls["belief_well_one_selects_index"] == 0
    assert controls["optimistic_comment_index"] == 1
    assert controls["label_reversal_observed"] is True
    assert controls["snapshot_mutation_max"] > 0
    assert controls["normal_numeric_order_completes"] is True
    assert controls["plot_excluded_grid_points"] == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"seed": -1},
        {"seed": 2**32},
        {"seed": True},
        {"agents": 0},
        {"agents": 1.2},
        {"days": 0},
        {"steps": -1},
    ],
)
def test_run_when_input_invalid(kwargs):
    # Given an invalid boundary value, when constructing the source run.
    with pytest.raises(SourceInputError):
        run_source_reconstruction(root=ROOT, **kwargs)
    # Then no numerical result was admitted.


@pytest.mark.parametrize(
    ("prior", "weights"),
    [
        ([1.0, 1.0], [1.0, 1.0]),
        ([0.5, 0.5], [-1.0, 1.0]),
        ([0.5, 0.5], [float("nan"), 1.0]),
        ([0.5, 0.5], [float("inf"), 1.0]),
        ([1.0], [1.0, 1.0]),
    ],
)
def test_posterior_when_input_invalid(prior, weights):
    # Given malformed numerical input, when the source-math helper is called.
    with pytest.raises(SourceInputError):
        source_posterior(np.array(prior), np.array(weights))
    # Then the invalid quantity cannot enter an audit.


def test_admission_when_source_is_modified(tmp_path):
    # Given a real copied notebook with one added byte.
    destination = tmp_path / "data/sources"
    destination.mkdir(parents=True)
    source = destination / "gratitude_original.ipynb"
    shutil.copyfile(ROOT / "data/sources/gratitude_original.ipynb", source)
    with source.open("ab") as stream:
        stream.write(b"\n")
    # When admission runs, then modified source is rejected before execution.
    with pytest.raises(SourceInputError, match="digest"):
        run_source_reconstruction(agents=1, root=tmp_path)


def test_minimum_dimensions_when_all_equal_one():
    # Given the smallest admitted source dimensions, when executed.
    result = run_source_reconstruction(0, 1, 1, 1, root=ROOT)
    # Then both selected source phases produce finite outputs of requested shape.
    assert result.baseline.shape == (1, 1, 5, 1)
    assert result.intervention.shape == (1, 1, 4, 1)
    assert np.isfinite(result.intervention).all()


def test_yarbus_real_source_replay_and_axes():

    first = run_yarbus_reconstruction(root=ROOT)
    replay = run_yarbus_reconstruction(root=ROOT)
    changed = run_yarbus_reconstruction(seed=43, root=ROOT)
    negative = run_yarbus_reconstruction(agent_type="negative", root=ROOT)
    np.testing.assert_array_equal(first.states, replay.states)
    np.testing.assert_array_equal(first.observations, replay.observations)
    assert not np.array_equal(first.states, changed.states)
    assert not np.array_equal(first.likelihood, negative.likelihood)
    for action in range(13):
        for current in range(13):
            expected = np.eye(13)[action]
            np.testing.assert_array_equal(first.transitions[action, :, current], expected)
    np.testing.assert_allclose(first.priors.sum(axis=0), 1)
    np.testing.assert_array_equal(first.priors[:, 1:].argmax(axis=0), first.states[1:])
    np.testing.assert_allclose(first.policies[:, :-1].sum(axis=0), 1)
    # Actual observations include outcomes impossible under declared process a1.
    assert np.count_nonzero(first.process[first.observations.astype(int), first.states] == 0) == 33
    # Independent source sampling oracle at the initial neutral state.
    assert first.observations[0] == np.random.RandomState(42).choice(3, p=first.likelihood[:, 10])
    assert first.process[:, 10].argmax() == 1
    entropy = -np.sum(first.likelihood * np.log(first.likelihood + 1e-10), axis=0)
    expected_efe = -first.likelihood.T @ np.array([2.0, 0.0, -2.0]) + 0.5 * entropy
    expected_efe += np.random.RandomState(42).normal(0, 0.1, 13)
    np.testing.assert_array_equal(first.initial_efe, expected_efe)


def test_yarbus_does_not_consume_global_random_stream():

    previous = np.random.get_state()  # noqa: NPY002 - test source global RNG isolation
    try:
        np.random.seed(111)  # noqa: NPY002 - test source global RNG isolation
        run_yarbus_reconstruction(steps=1)
        assert np.random.random() == np.random.RandomState(111).random()  # noqa: NPY002 - test source global RNG isolation
    finally:
        np.random.set_state(previous)  # noqa: NPY002 - test source global RNG isolation


@pytest.mark.parametrize(
    "kwargs",
    [
        {"seed": -1},
        {"seed": True},
        {"seed": 2**32},
        {"steps": 0},
        {"steps": 1.5},
        {"agent_type": "unknown"},
    ],
)
def test_yarbus_rejects_invalid_boundary(kwargs):

    with pytest.raises(SourceInputError):
        run_yarbus_reconstruction(root=ROOT, **kwargs)


def test_yarbus_rejects_changed_source(tmp_path):

    destination = tmp_path / "data/sources"
    destination.mkdir(parents=True)
    source = destination / "yarbus_original.ipynb"
    source.write_bytes((ROOT / "data/sources/yarbus_original.ipynb").read_bytes() + b"\n")
    with pytest.raises(SourceInputError, match="digest"):
        run_yarbus_reconstruction(root=tmp_path)


def test_gratitude_clamp_is_exact_first_three_nonnegative_observations():
    result = run_source_reconstruction(agents=3, root=ROOT)
    for agent in result.intervention:
        for day in agent:
            indices = np.flatnonzero(day[1] != 2)[:3]
            np.testing.assert_array_equal(day[2, indices], np.ones(len(indices)))
            np.testing.assert_array_equal(day[3, indices], np.zeros(len(indices)))
            remaining = np.ones(day.shape[1], dtype=bool)
            remaining[indices] = False
            assert np.all(day[2, remaining] < 1)


def test_explicit_wrong_root_never_falls_back_to_checkout(tmp_path: Path) -> None:
    """A supplied empty root must fail even while checkout source is available."""
    with pytest.raises(SourceInputError, match="Source notebook missing"):
        run_source_reconstruction(agents=1, root=tmp_path)
    with pytest.raises(SourceInputError, match="Source notebook missing"):
        run_yarbus_reconstruction(root=tmp_path)


def test_default_source_root_reconstructs_gratitude() -> None:
    result = run_source_reconstruction(agents=1, days=1, steps=1)
    assert result.baseline.shape == (1, 1, 5, 1)
