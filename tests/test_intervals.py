# Copyright (c) 2026 Daniel Ari Friedman
import json
from dataclasses import asdict

import numpy as np
import pytest

from thanks_for_nothing.estimation import StatisticalInputError, exact_sign_flip, paired_contrast
from thanks_for_nothing.intervals import mean_intervals


def test_constant_decimal_sample_has_exactly_zero_variance():
    result = mean_intervals(np.full((1, 64), -0.1), 1023, np.random.default_rng(17))

    assert result.standard_error == 0
    assert result.studentized.status == "degenerate_sample"
    assert result.studentized.degenerate_resamples == 1023
    assert result.analytic_low == result.analytic_high == -0.1


def test_decimal_resample_degeneracy_matches_independent_exact_range_oracle():
    values = np.asarray([[-0.1] * 63 + [0.9]], dtype=np.float64)
    indices = np.random.default_rng(17).integers(64, size=(1023, 1, 64))
    samples = values[0, indices[:, 0]]
    constant_draws = int(np.sum(np.max(samples, axis=1) == np.min(samples, axis=1)))
    result = mean_intervals(values, 1023, np.random.default_rng(17))

    assert constant_draws == 372
    assert result.standard_error == 0.015625
    assert result.studentized.status == "degenerate_resamples"
    assert result.studentized.degenerate_resamples == constant_draws
    assert result.studentized.low is result.studentized.high is None


def test_studentization_preserves_representable_large_stratum_translations():
    values = np.random.default_rng(12).integers(-32, 33, size=(3, 64)) / 8
    offsets = np.asarray([[2**30], [-(2**31)], [2**29]], dtype=np.float64)
    original = mean_intervals(values, 1023, np.random.default_rng(17))
    translated = mean_intervals(values + offsets, 1023, np.random.default_rng(17))
    shift = float(np.mean(offsets))

    assert translated.standard_error == original.standard_error
    assert translated.degrees_freedom == original.degrees_freedom
    assert translated.studentized.status == original.studentized.status == "available"
    ulp = abs(float(np.spacing(shift)))
    assert translated.studentized.low == pytest.approx(original.studentized.low + shift, rel=0, abs=ulp)
    assert translated.studentized.high == pytest.approx(
        original.studentized.high + shift, rel=0, abs=ulp
    )


def test_studentized_interval_transforms_with_location_and_positive_scale():
    values = np.random.default_rng(18).normal(0.2, 0.7, (3, 48))
    options = {"seed": 23, "bootstrap_draws": 511, "permutation_draws": 511}

    original = paired_contrast(values, **options)
    transformed = paired_contrast(2 * values + 3, **options)

    assert original.studentized.status == transformed.studentized.status == "available"
    assert transformed.studentized.low == pytest.approx(2 * original.studentized.low + 3)
    assert transformed.studentized.high == pytest.approx(2 * original.studentized.high + 3)
    assert original.studentized.low < original.mean_difference < original.studentized.high


def test_studentization_reports_constant_sample_without_inventing_an_interval():
    result = paired_contrast([[2.0] * 8], seed=3, bootstrap_draws=63, permutation_draws=63)

    assert result.studentized.status == "degenerate_sample"
    assert result.studentized.low is result.studentized.high is None
    assert result.studentized.degenerate_resamples == 63
    assert result.ci95_low == result.ci95_high == 2
    json.dumps(asdict(result), allow_nan=False)


def test_studentized_interval_uses_each_resample_variance_in_known_three_draw_example():
    result = paired_contrast([[0.0, 1.0, 4.0, 9.0]], seed=5, bootstrap_draws=3, permutation_draws=31)

    assert result.studentized.low == pytest.approx(1.7745144556216212, abs=1e-12)
    assert result.studentized.high == pytest.approx(5.752809157184796, abs=1e-12)


def test_studentization_retains_zero_variance_resamples_instead_of_discarding_them():
    result = paired_contrast([[0.0, 1.0]], seed=2, bootstrap_draws=255, permutation_draws=63)

    assert result.studentized.status == "degenerate_resamples"
    assert result.studentized.low is result.studentized.high is None
    assert 0 < result.studentized.degenerate_resamples < result.studentized.draws


@pytest.mark.parametrize(
    ("values", "expected"), [([[1, 2, 3]], 0.25), ([[-1, -2, -3]], 0.25), ([[0, 0]], 1)]
)
def test_exact_sign_flip_matches_hand_enumerated_tail_counts(values, expected):
    assert exact_sign_flip(values) == expected


def test_exhaustive_oracle_rejects_exponential_work_beyond_its_declared_limit():
    with pytest.raises(StatisticalInputError, match="at most 16"):
        exact_sign_flip([[1.0] * 17])
