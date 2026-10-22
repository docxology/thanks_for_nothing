# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace
from itertools import product

import numpy as np
import pytest

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.joint_contracts import JointBlock, JointDesign
from thanks_for_nothing.simultaneous import joint_region, quantile_mc_bracket


def _design(**updates):
    return JointDesign(
        seed=406,
        draws=1023,
        confidence=0.95,
        monte_carlo_confidence=0.99,
        calibration_experiments=4,
        calibration_units=16,
        calibration_draws=63,
    ).model_copy(update=updates)


def _block(values, *, exact=False, name="example"):
    data = np.asarray(values, dtype=np.float64)
    if data.ndim == 1:
        data = data[None, :, None]
    return JointBlock(
        name, tuple(str(i) for i in range(data.shape[-1])), data, (exact,) * data.shape[-1]
    )


def test_two_point_distribution_has_known_standard_error_and_maximum():
    result = joint_region((_block([-1.0, 1.0]),), _design())
    row = result.intervals[0]
    assert row.mean == 0
    assert row.standard_error == 1
    assert result.critical_value == 1
    assert (row.low, row.high) == (-1, 1)
    assert result.critical_mc_low == result.critical_mc_high == 1


def test_representable_translation_does_not_corrupt_near_constant_roots():
    values = (1 + (np.arange(128) % 5) * 2.0**-51)[None, :, None]
    centered = values - values[:, :1]
    translated = joint_region((_block(values),), _design())
    reference = joint_region((_block(centered),), _design())
    assert translated.critical_value == pytest.approx(reference.critical_value, abs=1e-12)
    assert translated.intervals[0].standard_error == reference.intervals[0].standard_error


def test_duplicate_opposite_columns_preserve_perfect_dependence():
    values = np.random.default_rng(412).normal(size=(2, 40, 1))
    one = joint_region((_block(values),), _design())
    redundant = joint_region(
        (_block(np.concatenate((values, -3 * values, 2 * values), axis=2)),), _design()
    )
    assert redundant.critical_value == pytest.approx(one.critical_value, abs=1e-12)
    original = one.intervals[0]
    opposite = redundant.intervals[1]
    assert opposite.low == pytest.approx(-3 * original.high)
    assert opposite.high == pytest.approx(-3 * original.low)


def test_destroying_pairing_changes_joint_critical_value():
    rng = np.random.default_rng(19)
    values = rng.normal(size=(1, 64, 1))
    paired = np.repeat(values, 6, axis=2)
    disrupted = np.concatenate([rng.permutation(values, axis=1) for _ in range(6)], axis=2)
    first = joint_region((_block(paired),), _design())
    second = joint_region((_block(disrupted),), _design())
    assert second.critical_value > first.critical_value + 0.3


def test_independent_blocks_do_not_share_bootstrap_indices():
    values = np.random.default_rng(15).normal(size=(1, 64, 1))
    single = joint_region((_block(values),), _design())
    independent = joint_region(
        (
            _block(values, name="one"),
            replace(_block(values, name="two"), keys=("second",)),
        ),
        _design(),
    )
    assert independent.critical_value > single.critical_value + 0.1


def test_mechanism_zero_and_accidental_constant_have_different_status():
    exact = _block([0, 0, 0, 0], exact=True, name="exact")
    constant = replace(_block([-0.01] * 4, name="rare"), keys=("rare",))
    variable = replace(_block([-1, 0, 1, 2], name="variable"), keys=("variable",))
    result = joint_region((exact, constant, variable), _design())
    assert result.status == "partial"
    assert result.intervals[0].status == "mechanism_exact"
    assert result.intervals[0].low == result.intervals[0].high == 0
    assert result.intervals[1].status == "unavailable_constant"
    assert result.intervals[1].low is result.intervals[1].high is None
    assert result.intervals[2].status == "estimated"
    all_exact = joint_region((exact,), _design())
    assert all_exact.status == "mechanism_exact"
    assert all_exact.critical_value is None
    assert all_exact.draws == 0
    unavailable = joint_region((constant,), _design())
    assert unavailable.status == "unavailable"
    assert unavailable.critical_value is None
    with pytest.raises(ContractError, match="mechanism-exact zero"):
        joint_region((_block([1, 1, 1, 1], exact=True),), _design())


@pytest.mark.parametrize("values", [[], [1], [0, float("nan")], [0, float("inf")]])
def test_invalid_unit_arrays_fail(values):
    with pytest.raises(ContractError, match="Joint blocks"):
        joint_region((_block(values),), _design())


def test_empty_and_duplicate_families_fail():
    block = _block([-1, 0, 1])
    with pytest.raises(ContractError, match="at least one"):
        joint_region((), _design())
    with pytest.raises(ContractError, match="distinct names"):
        joint_region((block, block), _design())
    with pytest.raises(ContractError, match="unique"):
        joint_region((block, replace(block, name="other")), _design())


def test_quantile_bracket_has_conservative_exact_discrete_coverage():
    covered = 0
    for sample in product((0.0, 1.0), repeat=6):
        low, high = quantile_mc_bracket(np.asarray(sample), 0.5, 0.8)
        covered += (low is None or low <= 0) and (high is None or high >= 0)
    assert covered / 64 >= 0.8
    assert quantile_mc_bracket(np.array([1.0, 2.0]), 0.95, 0.99) == (1.0, None)
    assert quantile_mc_bracket(np.array([1.0, 2.0]), 0.5, 0.99) == (None, None)
    with pytest.raises(ContractError, match="finite roots"):
        quantile_mc_bracket(np.array([float("nan")]), 0.95, 0.99)
