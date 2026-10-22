# Copyright (c) 2026 Daniel Ari Friedman
import json
from dataclasses import asdict, replace

import pytest

from thanks_for_nothing.calibration import build_calibration_audit, calibration_consistent
from thanks_for_nothing.contracts import Design
from thanks_for_nothing.experiments import run_study


def test_calibration_is_seeded_and_has_real_null_and_positive_controls():
    design = replace(
        run_study(replicates=2).design,
        calibration_replicates=12,
        calibration_sample_size=32,
        calibration_bootstrap_draws=127,
        calibration_permutation_draws=127,
    )
    first = build_calibration_audit(design)
    assert first == build_calibration_audit(design)
    assert all(first.controls.values())
    null, positive, *stressors = first.rows
    assert positive.rejection_rate > null.rejection_rate
    assert len(stressors) == 4
    assert any("violated" in row.sign_flip_assumption for row in stressors)
    assert any(row.strata == 5 for row in stressors)
    assert all(
        row.studentized_covered <= row.studentized_available <= row.experiments for row in first.rows
    )
    assert all(
        0 <= row.rejection_ci_low <= row.rejection_rate <= row.rejection_ci_high <= 1
        for row in first.rows
    )
    assert all(
        0 <= row.coverage_ci_low <= row.coverage_rate <= row.coverage_ci_high <= 1 for row in first.rows
    )
    assert json.loads(json.dumps(asdict(first), allow_nan=False))["rows"][0]["experiments"] == 12


def test_reference_gaussian_calibration_retains_known_answers_and_undercoverage():
    design = replace(
        run_study(replicates=2).design,
        calibration_replicates=128,
        calibration_sample_size=32,
        calibration_bootstrap_draws=511,
        calibration_permutation_draws=511,
    )
    audit = build_calibration_audit(design)
    null, positive, *_ = audit.rows
    assert audit.seed == 20268316
    assert null.covered == 115
    assert positive.covered == 114
    assert null.analytic_t_covered == 120
    assert positive.analytic_t_covered == 116
    assert all(row.experiments == 128 for row in audit.rows)
    assert all(
        row.analytic_t_coverage_ci_low <= row.analytic_t_coverage_rate <= row.analytic_t_coverage_ci_high
        for row in audit.rows
    )
    assert null.coverage_rate < 0.95
    assert positive.coverage_rate < 0.95


@pytest.fixture(scope="module")
def calibration_case():
    design = replace(
        run_study(replicates=2).design,
        calibration_replicates=4,
        calibration_bootstrap_draws=63,
        calibration_permutation_draws=63,
    )
    return Design.model_validate(asdict(design)), build_calibration_audit(design)


def test_calibration_admission_accepts_actual_declared_operating_records(calibration_case):
    declaration, audit = calibration_case
    assert calibration_consistent(audit, declaration)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed", -1),
        ("bootstrap_draws", 0),
        ("permutation_draws", 0),
        ("controls", {}),
    ],
)
def test_calibration_admission_rejects_mismatched_run_identity(calibration_case, field, value):
    declaration, audit = calibration_case
    assert not calibration_consistent(replace(audit, **{field: value}), declaration)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("experiments", -1),
        ("sample_size", -1),
        ("strata", 0),
        ("true_difference", 99.0),
        ("sign_flip_assumption", "wrong"),
        ("studentized_available", -1),
        ("studentized_covered", 99),
        ("rejections", -1),
        ("covered", -1),
        ("analytic_t_covered", -1),
        ("rejection_rate", -0.1),
        ("coverage_rate", -0.1),
        ("analytic_t_coverage_rate", -0.1),
        ("studentized_coverage_rate", -0.1),
        ("rejection_ci_low", -1),
        ("coverage_ci_high", 2),
        ("analytic_t_coverage_ci_high", 2),
        ("studentized_coverage_ci_low", -1),
        ("rejection_mcse", -1),
        ("coverage_mcse", -1),
    ],
)
def test_calibration_admission_rejects_inconsistent_count_rate_or_interval(
    calibration_case, field, value
):
    declaration, audit = calibration_case
    changed = replace(audit.rows[0], **{field: value})
    assert not calibration_consistent(replace(audit, rows=(changed, *audit.rows[1:])), declaration)


def test_calibration_admission_rejects_incomplete_fixture_identity(calibration_case):
    declaration, audit = calibration_case
    assert not calibration_consistent(replace(audit, rows=tuple(reversed(audit.rows))), declaration)


def test_calibration_admission_rejects_forged_exact_availability(calibration_case):
    declaration, audit = calibration_case
    changed = replace(audit.discrete_availability, exact_availability=1.0)
    assert not calibration_consistent(replace(audit, discrete_availability=changed), declaration)
