# Copyright (c) 2026 Daniel Ari Friedman
from math import sqrt

import numpy as np
import pytest
from pydantic import ValidationError

from tests.support.models import copy_models
from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.estimation import paired_contrast
from thanks_for_nothing.intervals import mean_intervals
from thanks_for_nothing.sampling_diagnostics import summarize_prefixes
from thanks_for_nothing.source_reconstruction import run_source_reconstruction


def test_declared_analysis_level_changes_real_intervals_without_changing_the_data(tmp_path):
    # Given
    models = copy_models(tmp_path)
    original = load_analysis(models)
    values = [[-3.0, -1.0, 1.0, 5.0], [-2.0, 0.0, 2.0, 6.0]]
    baseline = paired_contrast(
        values, seed=13, bootstrap_draws=255, permutation_draws=255, analysis=original
    )
    path = models / "analysis.gnn.md"
    path.write_text(path.read_text().replace('"alpha":0.05', '"alpha":0.2'))

    # When
    changed = paired_contrast(
        values, seed=13, bootstrap_draws=255, permutation_draws=255, analysis=load_analysis(models)
    )

    # Then
    assert changed.mean_difference == baseline.mean_difference
    assert changed.confidence == pytest.approx(0.8)
    assert changed.analytic_t_ci95_high - changed.analytic_t_ci95_low < (
        baseline.analytic_t_ci95_high - baseline.analytic_t_ci95_low
    )
    assert changed.mc_interval_confidence == pytest.approx(0.8)


@pytest.mark.parametrize(
    "parameters",
    [
        {"alpha": 0},
        {"alpha": 1},
        {"diagnostic_prefixes": [4, 2]},
        {"diagnostic_prefixes": [2, 2]},
        {"diagnostic_prefixes": [1, 2]},
    ],
)
def test_invalid_analysis_declarations_are_rejected(parameters):
    original = load_analysis().model_dump()

    with pytest.raises((ValidationError, ContractError)):
        AnalysisDesign.model_validate(original | parameters)


def test_missing_selected_analysis_source_is_fatal(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_analysis(tmp_path)


def test_declared_source_adapter_settings_reach_real_source_execution(tmp_path):
    models = copy_models(tmp_path)
    path = models / "analysis.gnn.md"
    path.write_text(
        path.read_text()
        .replace('"reconstruction_seed":2025', '"reconstruction_seed":19')
        .replace('"reconstruction_agents":1000', '"reconstruction_agents":3')
        .replace('"reconstruction_days":7', '"reconstruction_days":2')
        .replace('"reconstruction_steps":12', '"reconstruction_steps":4')
    )

    actual = run_source_reconstruction(analysis=load_analysis(models))

    assert actual.seed == 19
    assert actual.baseline.shape == (3, 2, 5, 4)


@pytest.mark.parametrize("confidence", [0, 1, -0.1, float("nan")])
def test_invalid_interval_confidence_is_rejected(confidence):
    with pytest.raises(ValueError, match="confidence"):
        mean_intervals(np.asarray([[1.0, 2.0]]), 31, np.random.default_rng(1), confidence=confidence)


def test_sampling_precision_matches_independent_stratified_arithmetic():
    values = np.asarray([[0, 2, 4, 6], [1, 3, 5, 7]], dtype=np.float64)
    design = AnalysisDesign.model_validate(
        load_analysis().model_dump() | {"diagnostic_prefixes": [2, 4]}
    )

    early, full = summarize_prefixes(values, design)

    assert (early.mean, full.mean) == (1.5, 3.5)
    assert early.monte_carlo_se == pytest.approx(sqrt(0.5))
    assert full.monte_carlo_se == pytest.approx(sqrt(5 / 6))
    assert full.strata == 2
    assert full.replicates_per_stratum == 4
    assert full.positive_fraction == 7 / 8
    assert not full.empirical_constant


def test_constant_sampling_record_is_marked_empirical_without_invented_variance():
    values = np.full((2, 64), -0.1, dtype=np.float64)

    points = summarize_prefixes(values, load_analysis())

    assert all(point.mean == pytest.approx(-0.1) for point in points)
    assert all(point.monte_carlo_se == 0 for point in points)
    assert all(point.empirical_constant for point in points)


@pytest.mark.parametrize("values", [[], [[1]], [[float("nan"), 1]], [[[1, 2]]]])
def test_invalid_precision_inputs_are_rejected(values):
    data = np.asarray(values, dtype=np.float64)

    with pytest.raises(ContractError):
        summarize_prefixes(data, load_analysis())
