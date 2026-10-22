# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace

import pytest
from pydantic import TypeAdapter

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_joint import GazeUncertainty, build_gaze_uncertainty
from thanks_for_nothing.joint_calibration import coverage_rate


def test_joint_family_preserves_original_estimands_and_exact_identities(small_gaze):
    _, _, gaze = small_gaze
    result = build_gaze_uncertainty(gaze)
    assert result.all_controls_pass
    assert len(result.region.intervals) == 58
    assert sum(row.status == "mechanism_exact" for row in result.region.intervals) == 10
    assert result.region.blocks == (("transfer", 5, 3), ("stationary", 1, 4), ("reversal", 1, 4))
    for original, joint in zip(gaze.contrasts, result.region.intervals, strict=True):
        assert original.intervals.mean == pytest.approx(joint.mean, abs=1e-14)
        assert original.intervals.standard_error == pytest.approx(joint.standard_error, abs=1e-14)
    assert TypeAdapter(GazeUncertainty).validate_json(record_json(result)) == result
    reordered = replace(
        gaze, transfer=tuple(reversed(gaze.transfer)), episodes=tuple(reversed(gaze.episodes))
    )
    assert build_gaze_uncertainty(reordered).region == result.region


@pytest.mark.parametrize("target", ["transfer", "episodes"])
@pytest.mark.parametrize("mutation", ["missing", "duplicate", "exposure"])
def test_incomplete_or_unpaired_vectors_are_rejected(small_gaze, target, mutation):
    _, _, gaze = small_gaze
    rows = getattr(gaze, target)
    if mutation == "missing":
        changed = rows[:-1]
    elif mutation == "duplicate":
        changed = (*rows, rows[0])
    else:
        changed = (replace(rows[0], exposure_sha256="altered-exposure"), *rows[1:])
    with pytest.raises(ContractError, match="uncertainty requires"):
        build_gaze_uncertainty(replace(gaze, **{target: changed}))


@pytest.mark.parametrize("target", ["transfer", "episodes"])
def test_semantic_identity_drift_cannot_be_licensed_as_exact(small_gaze, target):
    _, _, gaze = small_gaze
    if target == "transfer":
        rows = list(gaze.transfer)
        index = next(i for i, row in enumerate(rows) if row.condition == "absence_appreciation")
        rows[index] = replace(rows[index], post_locations=(1, *rows[index].post_locations[1:]))
        changed = replace(gaze, transfer=tuple(rows))
    else:
        rows = list(gaze.episodes)
        index = next(i for i, row in enumerate(rows) if row.condition == "sham")
        rows[index] = replace(rows[index], final_posterior=(0.1, 0.9, 0.0))
        changed = replace(gaze, episodes=tuple(rows))
    with pytest.raises(ContractError, match="Mechanism-exact"):
        build_gaze_uncertainty(changed)


def test_rate_bounds_match_exact_binomial_boundary_formulas():
    zero = coverage_rate(0, 4)
    full = coverage_rate(4, 4)
    assert zero.low == 0
    assert zero.high == pytest.approx(1 - 0.025**0.25)
    assert full.low == pytest.approx(0.025**0.25)
    assert full.high == 1
    assert zero.monte_carlo_se == full.monte_carlo_se == 0


def test_incomplete_source_contrast_family_cannot_be_silently_dropped(small_gaze):
    _, _, gaze = small_gaze
    with pytest.raises(ContractError, match="complete pointwise source family"):
        build_gaze_uncertainty(replace(gaze, contrasts=gaze.contrasts[:-1]))
