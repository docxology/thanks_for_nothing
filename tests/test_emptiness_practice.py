# Copyright (c) 2026 Daniel Ari Friedman
"""Real GNN edits, exact imported inference and falsifiable practice-policy controls."""

import math
from dataclasses import replace

import numpy as np
import pytest
from pydantic import ValidationError

from tests.support.models import edit_settings
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.emptiness_practice import build_practice_audit
from thanks_for_nothing.practice_contracts import PracticeDesign
from thanks_for_nothing.practice_controls import practice_controls
from thanks_for_nothing.practice_figures import practice_policies, practice_revision
from thanks_for_nothing.practice_findings import practice_findings
from thanks_for_nothing.practice_inference import admitted_priors, compare_priors, practice_probability
from thanks_for_nothing.specifications import load_model
from thanks_for_nothing.upstream_practice import build_upstream_practice_audit


def test_practice_replay_pairing_controls_and_real_figures(practice_models, tmp_path):
    audit = build_practice_audit(specification_dir=practice_models)
    assert audit == build_practice_audit(specification_dir=practice_models)
    assert audit.all_controls_pass
    assert all(audit.controls.values())
    assert len(audit.rows) == 2 * 4 * 12 * 5
    assert len(audit.contrasts) == 8
    assert all(math.isfinite(r.heldout_log_loss) for r in audit.rows)
    assert all(r.incurred_cost == audit.design.practice_cost for r in audit.rows if r.practiced)
    assert all(r.comparison.oracle_error < 1e-10 for r in audit.rows)
    assert all(
        r.heldout_loss_difference.mean == 0
        for r in audit.contrasts
        if r.condition in {"sham", "no_access"}
    )
    upstream = build_upstream_practice_audit()
    assert upstream.all_controls_pass
    assert not upstream.practice_deltas_enacted_upstream
    assert not upstream.revision_assessment_held_out
    write_record(tmp_path / "data/emptiness_practice.json", audit)
    write_record(tmp_path / "data/upstream_practice.json", upstream)
    figures = (
        practice_policies(audit, tmp_path / "figures"),
        practice_revision(audit, tmp_path / "figures"),
    )
    assert {f.name for f in figures} == {"practice_policies", "practice_revision"}
    assert all(f.publication_min_font_points >= 9.5 for f in figures)
    assert "pointwise" in practice_findings(audit)
    assert "failed" in practice_findings(replace(audit, all_controls_pass=False))


def test_changed_gnn_preference_and_access_are_consumed(practice_models):
    original = build_practice_audit(specification_dir=practice_models)
    edit_settings(practice_models, examinability_preference=0.0, metacognitive_access=0.0)
    changed = build_practice_audit(specification_dir=practice_models, replicates=3)
    assert changed.design.replicates == 3
    assert changed.model_sha256 != original.model_sha256
    assert changed.all_controls_pass
    assert all(not r.effective_access for r in changed.rows)
    assert all(c.heldout_loss_difference.mean == 0 for c in changed.contrasts)
    assert next(r for r in changed.rows if r.condition == "inquiry").action_probability < (
        next(r for r in original.rows if r.condition == "inquiry").action_probability
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("previous_observed_gain", 10.0),
        ("exposure_sha256", "forged"),
        ("forecast", 0.2),
    ],
)
def test_controls_reject_tampered_receipts(practice_models, field, value):
    audit = build_practice_audit(specification_dir=practice_models)
    row = next(r for r in audit.rows if r.condition == "no_access")
    changed = replace(row, **{field: value})
    rows = tuple(changed if r == row else r for r in audit.rows)
    controls = practice_controls(load_model("emptiness_practice", practice_models), audit.design, rows)
    assert not all(controls.values())


@pytest.mark.parametrize(
    "change",
    [
        {"conditions": ["rigid", "inquiry"]},
        {"conditions": ["rigid", "inquiry", "no_preference", "sham", "no_access", "sham"]},
        {"contexts": [{"name": "bad", "probabilities": [0.5, 0.5]}]},
        {
            "contexts": [
                {"name": "stationary", "probabilities": [1.0, 0.5]},
                {"name": "reversal", "probabilities": [0.5, 0.5]},
            ]
        },
        {
            "contexts": [
                {"name": "stationary", "probabilities": [0.5, 0.5]},
                {"name": "reversal", "probabilities": [0.5, 0.5, 0.5]},
            ]
        },
        {"replicates": 1},
    ],
)
def test_invalid_gnn_design_rejects(practice_models, change):
    edit_settings(practice_models, **change)
    with pytest.raises((ContractError, ValidationError)):
        build_practice_audit(specification_dir=practice_models)


def test_upstream_repertoire_admission_and_tensor_rejection(practice_models):
    model = load_model("emptiness_practice", practice_models)
    design = PracticeDesign.model_validate_json(model.parameters_json)
    restricted, opened = admitted_priors(model, design)
    assert restricted.tolist() == [0.5, 0.5, 0]
    assert opened.tolist() == pytest.approx([1 / 3] * 3)
    with pytest.raises(ContractError, match="positive binary"):
        admitted_priors(
            replace(model, tensors=model.tensors.model_copy(update={"A": ((0, 1, 0),)})), design
        )
    with pytest.raises(ContractError, match="neutral"):
        admitted_priors(replace(model, tensors=model.tensors.model_copy(update={"C": (1, 0)})), design)
    all_dual = design.model_dump()
    for item in all_dual["deployments"]:
        item["labels"] = ["self", "self", "env"]
    with pytest.raises(ContractError, match="proper restricted"):
        admitted_priors(model, PracticeDesign.model_validate(all_dual))
    duplicate = design.model_dump()
    duplicate["deployments"][2]["name"] = duplicate["deployments"][0]["name"]
    with pytest.raises(ContractError, match="distinct candidates"):
        admitted_priors(model, PracticeDesign.model_validate(duplicate))


def test_exact_free_energy_nats_and_extreme_support():
    channel = np.array([[0.9, 0.1], [0.1, 0.9]], dtype=np.float64)
    restricted = np.array([1.0, 0.0], dtype=np.float64)
    opened = np.array([0.5, 0.5], dtype=np.float64)
    result = compare_priors(channel, restricted, opened, (0, 24))
    expected = -math.log(0.5 * 0.1**24 + 0.5 * 0.9**24)
    assert result.open_free_energy == pytest.approx(expected, abs=1e-12)
    assert result.restricted_free_energy == pytest.approx(-24 * math.log(0.1), abs=1e-12)
    assert result.delta_free_energy == pytest.approx(result.delta_complexity - result.delta_accuracy)
    assert result.prefers_open
    assert not compare_priors(channel, restricted, opened, (24, 0)).prefers_open
    assert compare_priors(channel, restricted, opened, (0, 10000)).oracle_error < 1e-8


@pytest.mark.parametrize("probability", [0.5, 0.37])
@pytest.mark.parametrize("count", [0, 1, 12, 24])
def test_equal_evidence_retains_restriction_with_three_candidates(probability, count):
    channel = np.array([[probability] * 3, [1 - probability] * 3], dtype=np.float64)
    restricted = np.array([0.5, 0.5, 0.0], dtype=np.float64)
    opened = np.full(3, 1 / 3, dtype=np.float64)

    comparison = compare_priors(channel, restricted, opened, (count, 24 - count))

    assert not comparison.prefers_open
    expected = -count * math.log(probability) - (24 - count) * math.log1p(-probability)
    assert comparison.restricted_free_energy == pytest.approx(expected)
    assert comparison.open_free_energy == pytest.approx(expected)


@pytest.mark.parametrize("counts", [(-1, 2), (1.5, 2), (True, 2)])
def test_invalid_counts_reject(counts):
    channel = np.full((2, 2), 0.5, dtype=np.float64)
    prior = np.array([0.5, 0.5], dtype=np.float64)
    with pytest.raises(ContractError):
        compare_priors(channel, prior, prior, counts)


def test_policy_cost_preference_history_and_invalid_gain(practice_models):
    design = build_practice_audit(specification_dir=practice_models).design
    assert 0 < practice_probability(design, 0, 0) < practice_probability(design, 0.4, 0)
    assert practice_probability(design, 0.4, 0) < practice_probability(design, 0.4, 1)
    assert practice_probability(design, 1e6, 0) == 1
    costly = PracticeDesign.model_validate(design.model_dump() | {"practice_cost": 1e6})
    assert practice_probability(costly, 0, 0) == 0
    for invalid in (-1, float("nan"), float("inf")):
        with pytest.raises(ContractError):
            practice_probability(design, 0, invalid)


@pytest.mark.parametrize(("scale", "shift"), [(0.5, 0.1), (2.0, 0.3), (3.0, 0.0)])
def test_choice_policy_identifies_only_value_cost_and_gain_combinations(practice_models, scale, shift):
    design = build_practice_audit(specification_dir=practice_models).design
    transformed = PracticeDesign.model_validate(
        design.model_dump()
        | {
            "action_precision": design.action_precision / scale,
            "examinability_preference": scale * design.examinability_preference + shift,
            "practice_cost": scale * design.practice_cost + shift,
            "previous_gain_weight": scale * design.previous_gain_weight,
        }
    )
    for gain in (0.0, 0.03, 0.7, 2.0):
        assert practice_probability(design, design.examinability_preference, gain) == pytest.approx(
            practice_probability(transformed, transformed.examinability_preference, gain),
            abs=1e-14,
        )
    assert practice_probability(design, design.examinability_preference, 0) != practice_probability(
        design,
        design.examinability_preference + 0.3,
        0,
    )
