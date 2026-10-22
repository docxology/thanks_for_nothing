# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace
from typing import assert_never

import pytest

from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.experiments import run_study
from thanks_for_nothing.statistics import build_statistical_report


@pytest.fixture(scope="module")
def known_world_rows():
    rows = []
    effects = {0.1: -0.03, 0.3: -0.01, 0.5: 0.01, 0.7: 0.03, 0.9: 0.05}
    for row in run_study(replicates=3).rows:
        match row.condition:
            case Condition.POSITIVE:
                delta = effects[row.luckiness] + (row.replicate - 1) * 0.001
            case Condition.NO_RECALL | Condition.RANDOM | Condition.ABSENCE:
                delta = 0.0
            case unreachable:
                assert_never(unreachable)
        rows.append(replace(row, brier_post=row.brier_pre + delta))
    return tuple(rows)


def test_world_estimates_and_weighting_envelopes_match_known_paired_changes(known_world_rows):
    report = build_statistical_report(known_world_rows, seed=7, bootstrap_draws=63, permutation_draws=63)
    mixture = next(
        row
        for row in report.heterogeneity.weighting
        if row.endpoint == "brier_change" and row.second == Condition.NO_RECALL
    )
    strata = [
        row
        for row in report.heterogeneity.strata
        if row.endpoint == "brier_change" and row.second == Condition.NO_RECALL
    ]

    assert mixture.equal_grid.mean == pytest.approx(0.01)
    assert (mixture.convex_min, mixture.convex_max) == pytest.approx((-0.03, 0.05))
    assert (mixture.leave_one_out_min, mixture.leave_one_out_max) == pytest.approx((0, 0.02))
    assert [row.intervals.mean for row in strata] == pytest.approx([-0.03, -0.01, 0.01, 0.03, 0.05])
    assert [row.units for row in strata] == [3] * 5
    assert strata[0].q25 == pytest.approx(-0.0305)
    assert strata[0].q75 == pytest.approx(-0.0295)
    assert [row.positive_fraction for row in strata] == [0, 0, 1, 1, 1]
    assert len(report.contrasts) == 8


def test_diagnostics_preserve_pairing_when_source_rows_are_reordered(known_world_rows):
    options = {"seed": 31, "bootstrap_draws": 63, "permutation_draws": 63}

    forward = build_statistical_report(known_world_rows, **options)
    backward = build_statistical_report(tuple(reversed(known_world_rows)), **options)

    assert forward == backward


def test_single_world_has_no_leave_one_out_estimand(known_world_rows):
    rows = tuple(row for row in known_world_rows if row.luckiness == 0.1)

    report = build_statistical_report(rows, seed=7, bootstrap_draws=31, permutation_draws=31)

    assert all(row.leave_one_out_min is None for row in report.heterogeneity.weighting)
    assert all(row.leave_one_out_max is None for row in report.heterogeneity.weighting)
