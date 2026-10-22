# Copyright (c) 2026 Daniel Ari Friedman
"""Independent finite count checks using real admitted GNN declarations."""

import math
from dataclasses import replace
from fractions import Fraction

import pytest

from tests.support.models import edit_settings
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.emptiness_practice import build_practice_audit
from thanks_for_nothing.practice_exact import build_exact_decision_audit
from thanks_for_nothing.practice_figures import exact_decision
from thanks_for_nothing.practice_findings import exact_decision_findings, practice_interval_findings
from thanks_for_nothing.practice_inference import practice_probability


def test_exhaustive_count_decisions_have_independent_closed_form_and_exact_mass():
    audit = build_exact_decision_audit()
    assert audit.all_controls_pass
    assert len(audit.rows) == 25
    assert [r.zero_count for r in audit.rows if r.supports_open] == list(range(9))
    for row in audit.rows:
        k = row.zero_count
        likelihoods = [p**k * (1 - p) ** (24 - k) for p in map(Fraction, (".85", ".55", ".15"))]
        assert row.supports_open == (2 * likelihoods[2] > likelihoods[0] + likelihoods[1])
        ratio = 2 * sum(likelihoods) / (3 * sum(likelihoods[:2]))
        assert row.log_bayes_factor == pytest.approx(math.log(float(ratio)), abs=1e-12)
    rare = next(p for p in audit.operating_points if p.process_probability == 0.85)
    p = Fraction(85, 100)
    expected = sum(Fraction(math.comb(24, k)) * p**k * (1 - p) ** (24 - k) for k in range(9))
    actual = Fraction(int(rare.open_probability_numerator), int(rare.open_probability_denominator))
    assert actual == expected
    assert 0 < rare.open_probability < 2e-8
    assert rare.expected_loss_difference > 0
    assert all(sum(p.count_probabilities) == pytest.approx(1) for p in audit.operating_points)


def test_one_observation_oracle_consumes_gnn_and_policy_changes_do_not_change_it(practice_models):
    edit_settings(practice_models, calibration_samples=1)
    audit = build_exact_decision_audit(specification_dir=practice_models)
    assert [r.zero_count for r in audit.rows if r.supports_open] == [0]
    assert [p.open_probability for p in audit.operating_points] == pytest.approx([0.85, 0.15])
    assert audit.rows[0].restricted_forecast == pytest.approx((0.85 * 0.15 + 0.55 * 0.45) / 0.6)
    forecast = (0.85 * 0.15 + 0.55 * 0.45 + 0.15 * 0.85) / 1.45
    assert audit.rows[0].evidence_selected_forecast == pytest.approx(forecast)
    edit_settings(practice_models, metacognitive_access=0, practice_cost=4, examinability_preference=0)
    changed = build_exact_decision_audit(specification_dir=practice_models)
    assert changed.model_sha256 != audit.model_sha256
    assert replace(changed, model_sha256=audit.model_sha256) == audit


@pytest.mark.parametrize("probability", [0.0, 1.0])
def test_invalid_process_probability_rejected(practice_models, probability):
    edit_settings(practice_models, contexts=[{"name": "stationary", "probabilities": [probability] * 2}])
    with pytest.raises(ContractError, match="strictly between"):
        build_exact_decision_audit(specification_dir=practice_models)


def test_nonfinite_process_probability_is_rejected_by_real_upstream_admission(practice_models):
    edit_settings(
        practice_models, contexts=[{"name": "stationary", "probabilities": [float("nan")] * 2}]
    )
    with pytest.raises(ValueError, match="GNN settings require"):
        build_exact_decision_audit(specification_dir=practice_models)


def test_identical_channels_have_no_open_counts_or_gain(practice_models):
    path = practice_models / "emptiness_practice.gnn.md"
    source = path.read_text()
    source = source.replace("A=[[0.85,0.55,0.15],[0.15,0.45,0.85]]", "A=[[0.5,0.5,0.5],[0.5,0.5,0.5]]")
    path.write_text(source)
    audit = build_exact_decision_audit(specification_dir=practice_models)
    assert audit.all_controls_pass
    assert not any(row.supports_open for row in audit.rows)
    assert all(point.open_probability == 0 for point in audit.operating_points)
    assert all(point.log10_open_probability is None for point in audit.operating_points)
    assert all(point.expected_loss_difference == 0 for point in audit.operating_points)
    assert "counts none" in exact_decision_findings(audit)


def test_exact_figure_and_full_interval_reporting(practice_models, tmp_path):
    audit = build_exact_decision_audit(specification_dir=practice_models)
    write_record(tmp_path / "data/exact_decision.json", audit)
    record = exact_decision(audit, tmp_path / "figures")
    assert record.name == "exact_decision"
    assert record.source_artifacts == ("data/exact_decision.json",)
    assert record.publication_min_font_points >= 9.5
    text = exact_decision_findings(audit)
    assert "1.43362441e-08" in text
    assert "conditional on an effective inquiry" in text
    practice = build_practice_audit(specification_dir=practice_models)
    intervals = practice_interval_findings(practice)
    assert intervals.count("| Stationary /") == 4
    assert intervals.count("| Reversal /") == 4
    assert "Unavailable (degenerate sample)" in intervals
    contrast = practice.contrasts[0]
    invalid_interval = replace(
        contrast.heldout_loss_difference.studentized, status="available", low=None
    )
    invalid_contrast = replace(
        contrast,
        heldout_loss_difference=replace(contrast.heldout_loss_difference, studentized=invalid_interval),
    )
    with pytest.raises(ValueError, match="requires both bounds"):
        practice_interval_findings(replace(practice, contrasts=(invalid_contrast,)))
    design = practice.design
    shifted = design.model_copy(
        update={
            "practice_cost": design.practice_cost + 1,
            "examinability_preference": design.examinability_preference + 1,
        }
    )
    assert practice_probability(design, design.examinability_preference, 0) == pytest.approx(
        practice_probability(shifted, shifted.examinability_preference, 0)
    )
