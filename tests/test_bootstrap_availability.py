# Copyright (c) 2026 Daniel Ari Friedman
from itertools import product
from math import prod

import pytest

from thanks_for_nothing.bootstrap_availability import bernoulli_availability
from thanks_for_nothing.estimation import StatisticalInputError


def test_availability_matches_exhaustive_original_and_resampled_sequences():
    # Given
    n, p, draws = 3, 0.25, 2
    resamples = tuple(product(range(n), repeat=n))
    expected = 0.0
    for sample in product((0, 1), repeat=n):
        weight = prod(p if value else 1 - p for value in sample)
        valid = sum(
            all(len({sample[index] for index in indices}) == 2 for indices in sequence)
            for sequence in product(resamples, repeat=draws)
        )
        expected += weight * valid / len(resamples) ** draws

    # When
    actual = bernoulli_availability(n, p, draws)

    # Then
    assert actual.exact_availability == pytest.approx(expected, abs=1e-15)


def test_two_observation_availability_matches_hand_enumeration():
    # Given / When
    actual = bernoulli_availability(2, 0.5, 2)

    # Then
    assert actual.exact_availability == pytest.approx(1 / 8, abs=1e-15)
    assert actual.counts[0].interval_available_probability == 0
    assert actual.counts[-1].interval_available_probability == 0


def test_additional_resamples_reduce_strict_availability_without_changing_sample_law():
    # Given
    fewer = bernoulli_availability(16, 0.1, 31)

    # When
    more = bernoulli_availability(16, 0.1, 1023)

    # Then
    assert more.exact_availability < fewer.exact_availability
    assert [r.sample_probability for r in more.counts] == [r.sample_probability for r in fewer.counts]
    assert bernoulli_availability(16, 0.9, 1023).exact_availability == pytest.approx(
        more.exact_availability
    )


@pytest.mark.parametrize("probability", [0.0, 1.0])
def test_constant_population_never_supplies_studentization(probability):
    actual = bernoulli_availability(8, probability, 31)
    assert actual.exact_availability == 0


@pytest.mark.parametrize(
    ("n", "p", "draws"),
    [(1, 0.5, 3), (True, 0.5, 3), (4, -0.1, 3), (4, float("nan"), 3), (4, 0.5, 0)],
)
def test_invalid_availability_design_is_rejected(n, p, draws):
    with pytest.raises(StatisticalInputError):
        bernoulli_availability(n, p, draws)
