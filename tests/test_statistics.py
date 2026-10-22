# Copyright (c) 2026 Daniel Ari Friedman
import json
from dataclasses import asdict, replace

import numpy as np
import pytest

from thanks_for_nothing.experiments import run_study
from thanks_for_nothing.intervals import quantile_pair
from thanks_for_nothing.statistics import (
    StatisticalInputError,
    build_statistical_report,
    holm_adjust,
    paired_contrast,
)


def test_paired_zero_null_is_exact_and_serializable():
    result = paired_contrast([[0.0] * 16] * 3, seed=4, bootstrap_draws=128, permutation_draws=511)
    assert result.mean_difference == result.ci95_low == result.ci95_high == 0
    assert result.p_value == 1
    assert result.permutation_exceedances == 511
    assert result.cohen_dz == 0
    assert result.tied_fraction == 1
    json.dumps(asdict(result), allow_nan=False)


def test_stratified_bootstrap_preserves_each_fixed_stratum_weight():
    result = paired_contrast(
        [[1.0] * 10, [-1.0] * 10], seed=1, bootstrap_draws=64, permutation_draws=127
    )
    assert result.mean_difference == result.ci95_low == result.ci95_high == 0
    assert result.p_value == 1
    assert result.positive_fraction == 0.5


def test_real_positive_and_negative_controls_are_detected_symmetrically():
    values = np.linspace(0.7, 1.3, 32).reshape(2, 16)
    positive = paired_contrast(values, seed=7, bootstrap_draws=512, permutation_draws=1023)
    negative = paired_contrast(-values, seed=7, bootstrap_draws=512, permutation_draws=1023)
    assert positive.ci95_low > 0
    assert negative.ci95_high < 0
    assert positive.p_value == negative.p_value == 1 / 1024
    assert positive.mean_difference == pytest.approx(-negative.mean_difference)
    assert positive.mc_tail_ci_high < 0.01


def test_degenerate_nonzero_control_retains_finite_json():
    result = paired_contrast([[1.0] * 16], seed=1, bootstrap_draws=64, permutation_draws=127)
    assert result.cohen_dz is None
    assert result.ci95_low == result.ci95_high == 1
    json.dumps(asdict(result), allow_nan=False)


def test_seeded_replay_and_monte_carlo_resolution():
    values = [[-0.3, 0.2, 0.5, -0.1, 0.8, -0.2]]
    first = paired_contrast(values, seed=23, bootstrap_draws=99, permutation_draws=127, family_size=8)
    second = paired_contrast(values, seed=23, bootstrap_draws=99, permutation_draws=127, family_size=8)
    changed = paired_contrast(values, seed=24, bootstrap_draws=99, permutation_draws=127, family_size=8)
    assert first == second
    assert first != changed
    assert first.p_resolution == 1 / 128
    assert first.mc_interval_confidence == 1 - 0.05 / 8


@pytest.mark.parametrize("values", [[], [1, 2], [[1]], [[1, np.inf]], [[np.nan, 1]]])
def test_invalid_paired_data_rejected(values):
    with pytest.raises(StatisticalInputError):
        paired_contrast(values, seed=1, bootstrap_draws=32, permutation_draws=31)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed", -1),
        ("seed", True),
        ("bootstrap_draws", 0),
        ("permutation_draws", 1.2),
        ("family_size", 0),
    ],
)
def test_invalid_monte_carlo_design_rejected(field, value):
    design = {"seed": 1, "bootstrap_draws": 32, "permutation_draws": 31, "family_size": 1}
    design[field] = value
    with pytest.raises(StatisticalInputError):
        paired_contrast([[1, 2]], **design)


def test_holm_adjustment_matches_hand_calculation_and_restores_order():
    assert holm_adjust([0.03, 0.01, 0.04]) == pytest.approx((0.06, 0.03, 0.06))
    assert holm_adjust([1, 0]) == (1.0, 0.0)


@pytest.mark.parametrize("values", [[], [np.nan], [-0.1], [1.01], [[0.1]]])
def test_invalid_multiple_testing_probabilities_rejected(values):
    with pytest.raises(StatisticalInputError):
        holm_adjust(values)


@pytest.mark.parametrize("draws", [1, 2, 5, 40])
def test_percentile_interpolation_matches_numpy_reference(draws):
    values = np.array([[0.1, -0.3, 0.8], [-0.5, 0.4, 0.2]])
    indices = np.random.default_rng(19).integers(3, size=(draws, 2, 3))
    means = np.take_along_axis(values[None, :, :], indices, axis=2).mean(axis=(1, 2))
    result = paired_contrast(values, seed=19, bootstrap_draws=draws, permutation_draws=31)
    expected = np.quantile(means, [0.025, 0.975])
    assert quantile_pair(means, (0.025, 0.975)) == tuple(expected)
    rounding_bound = 4 * np.finfo(np.float64).eps * float(np.max(np.abs(values)))
    np.testing.assert_allclose(
        [result.ci95_low, result.ci95_high], expected, rtol=0, atol=rounding_bound
    )


def test_balanced_report_retains_all_eight_contrasts_and_rejects_unmatched_exposures():
    rows = run_study(replicates=2).rows
    options = {"seed": 7, "bootstrap_draws": 31, "permutation_draws": 31}
    report = build_statistical_report(rows, **options)
    assert len(report.contrasts) == 8
    assert all(report.controls.values())
    assert report == build_statistical_report(rows, **options)
    changed = (replace(rows[0], exposure_sha256="wrong"), *rows[1:])
    with pytest.raises(StatisticalInputError, match="exogenous exposure"):
        build_statistical_report(changed, **options)
    changed = (replace(rows[0], paired_id="wrong"), *rows[1:])
    with pytest.raises(StatisticalInputError, match="paired identifiers"):
        build_statistical_report(changed, **options)
    with pytest.raises(StatisticalInputError, match="duplicate"):
        build_statistical_report((*rows, rows[0]), **options)
    with pytest.raises(StatisticalInputError, match="four-condition"):
        build_statistical_report(rows[1:], **options)
    with pytest.raises(StatisticalInputError, match="complete paired"):
        build_statistical_report((), **options)


def test_analytic_interval_matches_single_gaussian_stratum_formula():
    result = paired_contrast([[0.0, 1.0, 2.0, 3.0]], seed=4, bootstrap_draws=31, permutation_draws=31)
    expected_se = (5 / 12) ** 0.5
    critical_df3 = 3.182446305284263
    assert result.analytic_t_degrees_freedom == 3
    assert result.analytic_t_standard_error == pytest.approx(expected_se)
    assert result.analytic_t_ci95_low == pytest.approx(1.5 - critical_df3 * expected_se)
    assert result.analytic_t_ci95_high == pytest.approx(1.5 + critical_df3 * expected_se)


def test_analytic_stratified_variance_uses_within_stratum_uncertainty():
    result = paired_contrast(
        [[0.0, 2.0, 4.0], [0.0, 4.0, 8.0]], seed=4, bootstrap_draws=31, permutation_draws=31
    )
    assert result.analytic_t_standard_error == pytest.approx((5 / 3) ** 0.5)
    assert result.analytic_t_degrees_freedom == pytest.approx(50 / 17)
    constant = paired_contrast([[1.0] * 3, [-1.0] * 3], seed=4, bootstrap_draws=31, permutation_draws=31)
    assert constant.analytic_t_standard_error == 0
    assert constant.analytic_t_degrees_freedom is None
    assert constant.analytic_t_ci95_low == constant.analytic_t_ci95_high == 0
