# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace

import numpy as np
import pytest
from pydantic import TypeAdapter

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_active import GazeExposure, gaze_policy, run_gaze_episode
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_design import load_gaze_task
from thanks_for_nothing.gaze_transfer import build_transfer
from thanks_for_nothing.source_yarbus import run_yarbus_cohort


def exposure(task, candidate=2):
    rng = np.random.default_rng(19)
    return GazeExposure(
        "example",
        0,
        0,
        candidate,
        rng.random(task.design.steps),
        rng.random((task.design.steps, 3)),
        "unit-known-answer",
    )


def test_source_five_run_before_percentages():
    source = run_yarbus_cohort(load_gaze_task().design)
    assert source.positive_percent == pytest.approx([82.14, 10.98, 6.88], abs=1e-12)
    assert source.negative_percent == pytest.approx([54.62, 11.80, 33.58], abs=1e-12)
    assert source.published_before_matches
    assert source.after_intervention_available is False
    assert len(source.positive_states) == len(source.negative_states) == 5
    assert all(len(run) == 1000 and run[0] == 10 for run in source.positive_states)


def test_admitted_small_audit_and_intervals(small_gaze):
    _, experiment, audit = small_gaze
    assert audit.all_controls_pass
    assert all(audit.controls.values())
    assert len(audit.transfer) == 2 * len(experiment.study.rows)
    assert len(audit.episodes) == 2 * 4 * 3 * 6
    assert len(audit.contrasts) == 16 + 42
    assert TypeAdapter(GazeAudit).validate_json(record_json(audit)) == audit
    nulls = [row for row in audit.contrasts if row.condition in ("absence_appreciation", "sham")]
    assert nulls
    for row in nulls:
        assert row.intervals.mean == row.intervals.percentile_low == row.intervals.percentile_high == 0
        assert row.intervals.studentized.status == "degenerate_sample"
        assert row.intervals.studentized.low is None
    assert {row.units for row in audit.contrasts if row.experiment == "active"} == {4}
    assert {row.units for row in audit.contrasts if row.experiment == "transfer"} == {15}


def test_episode_matches_direct_product_and_balanced_risk(small_gaze):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    draw = exposure(task)
    row = run_gaze_episode(task, draw, "inquiry_open")
    posterior = task.open_prior.copy()
    risks = []
    counts = np.bincount(task.design.regions, minlength=3)
    for location, outcome in zip(row.locations, row.observations, strict=True):
        forecast = task.channels @ posterior
        risks.append(
            -sum(
                counts[region]
                / 13
                * sum(
                    task.channels[region, observation, draw.true_candidate]
                    * np.log(forecast[region, observation])
                    for observation in range(3)
                )
                for region in range(3)
            )
        )
        posterior *= task.channels[task.design.regions[location], outcome]
        posterior /= posterior.sum()
    assert row.final_posterior == pytest.approx(posterior, abs=1e-12)
    assert row.mean_balanced_log_loss == pytest.approx(float(np.mean(risks)), abs=1e-12)
    assert row.native_evidence_max_error < 1e-12


def test_family_support_and_exact_sham(small_gaze):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    draw = exposure(task)
    rigid = run_gaze_episode(task, draw, "pragmatic_restricted")
    sham = run_gaze_episode(task, draw, "sham")
    blocked = run_gaze_episode(task, draw, "inquiry_restricted")
    assert replace(sham, condition="pragmatic_restricted") == rigid
    assert rigid.final_posterior[2] == blocked.final_posterior[2] == 0
    opened = run_gaze_episode(task, draw, "inquiry_open")
    assert opened.final_posterior[2] > 0
    uniform = run_gaze_episode(task, draw, "uniform_open")
    assert len(uniform.locations) == task.design.steps


def test_zero_information_weight_is_exact_policy_ablation(small_gaze):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    task = replace(task, design=task.design.model_copy(update={"information_weight": 0.0}))
    draw = exposure(task)
    inquiry = run_gaze_episode(task, draw, "inquiry_open")
    pragmatic = run_gaze_episode(task, draw, "pragmatic_open")
    assert replace(inquiry, condition="pragmatic_open") == pragmatic


def test_candidate_permutation_preserves_sampling_and_losses(small_gaze):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    order = [2, 0, 1]
    permuted = replace(
        task,
        channels=task.channels[:, :, order],
        restricted_prior=task.restricted_prior[order],
        open_prior=task.open_prior[order],
    )
    draw = exposure(task)
    first = run_gaze_episode(task, draw, "inquiry_open")
    second = run_gaze_episode(permuted, replace(draw, true_candidate=0), "inquiry_open")
    assert first.locations == second.locations
    assert first.observations == second.observations
    assert first.mean_balanced_log_loss == pytest.approx(second.mean_balanced_log_loss, abs=1e-12)
    assert np.array(first.final_posterior)[order] == pytest.approx(second.final_posterior)


def test_identical_channels_provide_no_evidence(small_gaze):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    channels = np.broadcast_to(np.array([0.4, 0.3, 0.3])[None, :, None], (3, 3, 3)).copy()
    task = replace(task, channels=channels)
    row = run_gaze_episode(task, exposure(task), "inquiry_open")
    assert row.final_posterior == pytest.approx(task.open_prior, abs=1e-12)
    assert row.mean_information_gain == pytest.approx(0, abs=1e-14)


@pytest.mark.parametrize("value", [float("nan"), -0.1, 1.0])
def test_invalid_potential_outcomes_fail(small_gaze, value):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    draw = exposure(task)
    invalid = replace(draw, action_uniforms=np.full(task.design.steps, value))
    with pytest.raises(ContractError, match="Gaze exposure"):
        run_gaze_episode(task, invalid, "inquiry_open")


def test_policy_rejects_wrong_support_and_location(small_gaze):
    directory, _, _ = small_gaze
    task = load_gaze_task(directory)
    for posterior, location in ((np.array([0.0, 0.0, 0.0]), 0), (task.open_prior, 99)):
        with pytest.raises(ContractError, match="Gaze policy"):
            gaze_policy(task, posterior, location)


def test_transfer_is_learned_and_valuation_control_is_exact(small_gaze):
    directory, experiment, _ = small_gaze
    rows, hashes = build_transfer(experiment, load_gaze_task(directory), directory)
    assert len(hashes) == 2
    assert len(set(hashes)) == 2
    assert any(row.pre_policy != row.post_policy for row in rows)
    originals = {(row.paired_id, row.condition.value): row for row in experiment.study.rows}
    for row in rows:
        original = originals[row.paired_id, row.condition]
        assert row.prior_well == original.pre_world_well
        assert row.posterior_well == original.post_world_well
        assert row.exposure_sha256 == original.exposure_sha256
    baseline = {(row.bridge, row.paired_id): row for row in rows if row.condition == "no_recall"}
    for row in rows:
        if row.condition == "absence_appreciation":
            assert row.post_policy == baseline[row.bridge, row.paired_id].post_policy
            assert row.post_locations == baseline[row.bridge, row.paired_id].post_locations


def test_direct_transfer_does_not_consume_assessment_readout(small_gaze):
    directory, experiment, _ = small_gaze
    task = load_gaze_task(directory)
    original, _ = build_transfer(experiment, task, directory)
    altered = replace(
        experiment,
        study=replace(
            experiment.study,
            rows=tuple(
                replace(row, pre_world_well=0.1, post_world_well=0.9) for row in experiment.study.rows
            ),
        ),
    )
    changed, _ = build_transfer(altered, task, directory)
    for first, second in zip(original, changed, strict=True):
        if first.bridge == "likelihood":
            assert first.pre_policy == second.pre_policy
            assert first.post_policy == second.post_policy
        else:
            assert first.pre_policy != second.pre_policy
            assert first.post_policy != second.post_policy
