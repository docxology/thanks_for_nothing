# Copyright (c) 2026 Daniel Ari Friedman
"""Absence is observed evidence; valuation and missingness are distinct."""

import json
from dataclasses import asdict

import pytest

from tests.support.models import copy_models
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.nothingness import build_nothingness_audit, counterfactual_value


def test_operational_controls():
    audit = build_nothingness_audit()
    assert audit.all_controls_pass
    assert audit.missing_kl_bits == 0
    assert audit.observed_absence_kl_bits > 0
    assert audit.observed_absence_posterior[0] == pytest.approx(0.54 / 0.62)
    assert audit.blackwell_original_risk < audit.blackwell_erasure_risk
    json.dumps(asdict(audit), allow_nan=False)
    assert counterfactual_value(0.2, 3, 1) == pytest.approx(-0.4)


@pytest.mark.parametrize("args", [(-0.1, 1), (1.1, 1), (0.3, -1), (0.3, 1, -1), (float("nan"), 1)])
def test_invalid_reference(args):
    with pytest.raises(ContractError):
        counterfactual_value(*args)


def test_uninformative_source_breaks_informative_gate(tmp_path):
    copy_models(tmp_path)
    path = tmp_path / "nothingness.gnn.md"
    path.write_text(path.read_text().replace("A=[[0.9,0.2],[0.1,0.8]]", "A=[[0.5,0.5],[0.5,0.5]]"))
    result = build_nothingness_audit(specification_dir=tmp_path)
    assert not result.controls["observed_absence_informative"]
    assert not result.all_controls_pass
