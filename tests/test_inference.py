# Copyright (c) 2026 Daniel Ari Friedman
"""Independent numerical examples and rejecting controls."""

import numpy as np
import pytest

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.inference import cumulative, learn, normalize_counts, optimism, posterior, score


@pytest.mark.parametrize(
    ("axis", "expected"),
    [
        (None, [0.2, 0.9, 1.7, 2.0]),
        (0, [[0.2, 0.7], [1.0, 1.0]]),
        (1, [[0.2, 0.9], [0.8, 1.1]]),
        (-1, [[0.2, 0.9], [0.8, 1.1]]),
    ],
)
def test_cumulative_native_axes_and_input_preservation(axis, expected):
    values = np.array([[0.2, 0.7], [0.8, 0.3]], dtype=np.float64)
    before = values.copy()
    result = cumulative(values, axis=axis)
    np.testing.assert_allclose(result, expected)
    np.testing.assert_array_equal(values, before)
    assert result.dtype == np.float64
    assert not np.shares_memory(result, values)


def test_cumulative_invalid_axis_is_rejected_by_native_operation():
    with pytest.raises(np.exceptions.AxisError):
        cumulative(np.array([0.2, 0.8]), axis=1)


def test_bayes_missing_and_finite_precision():
    likelihood = np.array([[0.7, 0.2], [0.1, 0.1], [0.2, 0.7]])
    prior = np.array([0.5, 0.5])
    np.testing.assert_allclose(posterior(likelihood, prior, 0), [7 / 9, 2 / 9])
    q = posterior(likelihood, prior, 0, precision=4)
    assert q[0] == pytest.approx(0.7**4 / (0.7**4 + 0.2**4))
    assert 0 < q[0] < 1
    np.testing.assert_array_equal(posterior(likelihood, prior, None), prior)
    np.testing.assert_allclose(posterior(likelihood, prior, 1), prior)


@pytest.mark.parametrize(
    ("likelihood", "prior", "o", "precision"),
    [
        ([[0.7, 0.2], [0.1, 0.1], [0.2, 0.7]], [0.5, 0.5], -1, 1),
        ([[0.7, 0.2], [0.1, 0.1], [0.2, 0.7]], [0.5, 0.5], 3, 1),
        ([[0.7, 0.2], [0.1, 0.1], [0.2, 0.7]], [0.5, 0.5], 0, 0),
        ([[0.7, 0.2], [0.1, 0.1], [0.2, 0.7]], [0.5, 0.5], 0, float("nan")),
        ([[1, 0], [0, 1]], [0, 1], 0, 1),
        ([[1, 0], [0, 1]], [1, 1], 0, 1),
        ([[1, 0], [0, 1]], [-1, 2], 0, 1),
        ([[1, 0], [0, 1]], [0.5], 0, 1),
        ([[1, 0], [0, float("nan")]], [0.5, 0.5], 0, 1),
        ([[2, 0], [-1, 1]], [0.5, 0.5], 0, 1),
        ([[1, 0], [1, 1]], [0.5, 0.5], 0, 1),
        ([1, 0], [0.5, 0.5], 0, 1),
    ],
)
def test_invalid_categorical_contract(likelihood, prior, o, precision):
    with pytest.raises(ContractError):
        posterior(
            np.asarray(likelihood, dtype=float), np.asarray(prior, dtype=float), o, precision=precision
        )


def test_pseudocount_update_and_scores():
    counts = np.array([[7.0, 2.0], [1.0, 1.0], [2.0, 7.0]])
    updated = learn(counts, 0, np.array([0.8, 0.2]), 2.0, 1.0)
    np.testing.assert_allclose(updated[0], [8.6, 2.4])
    np.testing.assert_allclose(counts[0], [7, 2])
    normalized = normalize_counts(updated)
    np.testing.assert_allclose(normalized.sum(axis=0), 1)
    result = score(
        np.array([[0.8, 0.2], [0.2, 0.8]]), np.array([0.5, 0.5]), np.array([0, 1]), np.array([0, 1])
    )
    assert result.brier == pytest.approx(0.04)
    assert result.nll == pytest.approx(-np.log(0.5))
    assert result.world_well == pytest.approx(0.5)
    for bad in (np.array([1.0, 2.0]), np.array([[0.0, 1.0]]), np.array([[float("inf")]])):
        with pytest.raises(ContractError):
            normalize_counts(bad)


def test_optimism_readout_declared_mapping():
    priors = np.array([0.2, 0.5, 0.8])
    well = np.array([[0.8, 0.4], [0.2, 0.6]])
    poor = np.array([[0.6, 0.2], [0.4, 0.8]])
    assert optimism(1, priors, well, poor) != optimism(0, priors, well, poor)
    assert optimism(0.5, priors, well, poor) == pytest.approx(0, abs=1e-12)


def test_frozen_scoring_repeated_categories_matches_direct_bayes_arithmetic():
    likelihood = np.asarray([[0.65, 0.15], [0.05, 0.55], [0.3, 0.3]])
    prior = np.asarray([0.4, 0.6])
    observations = np.asarray([2, 0, 0, 1, 2, 1, 1])
    states = np.asarray([0, 1, 0, 1, 1, 0, 1])
    well = np.asarray([0.4, 0.26 / 0.35, 0.26 / 0.35, 0.02 / 0.35, 0.4, 0.02 / 0.35, 0.02 / 0.35])
    probabilities = np.asarray([0.3, 0.35, 0.35, 0.35, 0.3, 0.35, 0.35])

    actual = score(likelihood, prior, observations, states)

    assert actual.world_well == pytest.approx(float(np.mean(well)))
    assert actual.brier == pytest.approx(float(np.mean((well - (states == 0)) ** 2)))
    assert actual.nll == pytest.approx(float(-np.mean(np.log(probabilities))))
    entropy = -well * np.log(well) - (1 - well) * np.log(1 - well)
    assert actual.entropy == pytest.approx(float(np.mean(entropy)))


def test_frozen_scoring_does_not_condition_on_an_unobserved_unsupported_category():
    actual = score(
        np.asarray([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]),
        np.asarray([0.5, 0.5]),
        np.asarray([0, 1, 0, 1, 1]),
        np.asarray([0, 0, 1, 1, 1]),
    )

    assert actual.brier == pytest.approx(0.4)
    assert actual.world_well == pytest.approx(0.4)
    assert actual.entropy == 0
    assert actual.nll == pytest.approx(float(np.log(2)))


@pytest.mark.parametrize(
    ("observations", "states"), [([], []), ([0], []), ([[0, 1]], [0, 1]), ([0, 1], [[0, 1]])]
)
def test_scoring_rejects_unmatched_empty_and_nonvector_units(observations, states):
    with pytest.raises(ContractError, match="matched nonempty"):
        score(
            np.eye(2),
            np.asarray([0.5, 0.5]),
            np.asarray(observations, dtype=np.int64),
            np.asarray(states, dtype=np.int64),
        )
