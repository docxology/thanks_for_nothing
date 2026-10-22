# Copyright (c) 2026 Daniel Ari Friedman
"""Real native dependency execution and finite-policy receipt controls."""

import json
from dataclasses import asdict

import numpy as np
import pytest

from tests.support.models import copy_models
from thanks_for_nothing.attention import (
    AttentionParameters,
    NativeReceipt,
    _fixed_process,
    _native,
    _valid,
    build_attention_audit,
)
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.specifications import load_model


@pytest.mark.integration
def test_native_gnn_execution(tmp_path):
    audit = build_attention_audit(output_dir=tmp_path)
    assert audit.all_controls_pass
    json.dumps(asdict(audit), allow_nan=False)
    assert len(list(tmp_path.glob("*/simulation_results.json"))) == 4
    assert audit.rows[0].positive_mass != audit.rows[1].positive_mass
    for row in audit.rows:
        assert row.positive_mass + row.negative_mass + row.neutral_mass == pytest.approx(1, abs=1e-6)
    invalid = NativeReceipt(
        success=True,
        observations=(0,),
        actions=(99,),
        beliefs=((1.0,) * 13,),
        policy_posterior=((1.0,) * 13,),
    )
    model = load_model("attention_positive")
    assert not _valid(invalid, 1, len(model.tensors.D), len(model.tensors.B[0][0]), len(model.tensors.A))


def test_declared_attention_cardinality_is_consumed(tmp_path):
    copy_models(tmp_path)
    for name in ("attention_positive", "attention_negative"):
        path = tmp_path / f"{name}.gnn.md"
        source = path.read_text()
        model = load_model(name, tmp_path)
        assignments = {
            "A": np.asarray(model.tensors.A)[:, :4].tolist(),
            "B": np.repeat(np.eye(4)[:, :, None], 4, axis=2).tolist(),
            "C": list(model.tensors.C),
            "D": [0.25] * 4,
        }
        for key, value in assignments.items():
            line = next(line for line in source.splitlines() if line.startswith(key + "="))
            source = source.replace(line, key + "=" + json.dumps(value))
        for old, new in (
            ("A[3,13,", "A[3,4,"),
            ("B[13,13,13,", "B[4,4,4,"),
            ("D[13,", "D[4,"),
            ("s[13,", "s[4,"),
            ("u[13,", "u[4,"),
        ):
            source = source.replace(old, new)
        line = next(line for line in source.splitlines() if line.startswith("settings="))
        settings = json.loads(line[9:])
        settings[0]["parameters"].update(
            num_timesteps=3,
            process_likelihood=np.asarray(model.tensors.A)[:, :4].tolist(),
            positive_locations=[0],
            negative_locations=[1],
            neutral_locations=[2, 3],
        )
        path.write_text(source.replace(line, "settings=" + json.dumps(settings)))
    model = load_model("attention_positive", tmp_path)
    parameters = AttentionParameters.model_validate_json(model.parameters_json)
    row = _fixed_process(model, parameters)
    assert np.asarray(row.beliefs).shape == (parameters.num_timesteps, len(model.tensors.D))
    assert np.asarray(row.policy_posterior).shape == (parameters.num_timesteps, 4)
    receipt = _native(model, parameters, tmp_path / "native")
    assert _valid(receipt, parameters.num_timesteps, 4, 4, 3)


def test_attention_declared_process_rejections(tmp_path):
    copy_models(tmp_path)
    path = tmp_path / "attention_negative.gnn.md"
    path.write_text(path.read_text().replace('"random_seed":73', '"random_seed":74'))
    with pytest.raises(ContractError, match="identical"):
        build_attention_audit(specification_dir=tmp_path, output_dir=tmp_path / "receipts")
    model = load_model("attention_positive")
    params = AttentionParameters.model_validate_json(model.parameters_json)
    bad = params.model_copy(update={"process_likelihood": ((1.0,),)})
    with pytest.raises(ContractError, match="likelihood"):
        _fixed_process(model, bad)
    bad = params.model_copy(update={"positive_locations": (0,)})
    with pytest.raises(ContractError, match="partition"):
        _fixed_process(model, bad)


def test_invalid_process_fails_before_native_execution(tmp_path):
    copy_models(tmp_path)
    for name in ("attention_positive", "attention_negative"):
        path = tmp_path / f"{name}.gnn.md"
        text = path.read_text()
        original = '"process_likelihood":[[0.7,0.7,0.7,0.7,0.7'
        assert original in text
        path.write_text(text.replace(original, '"process_likelihood":[[1.7,0.7,0.7,0.7,0.7'))
    receipts = tmp_path / "receipts"
    with pytest.raises(ContractError, match="normalized"):
        build_attention_audit(specification_dir=tmp_path, output_dir=receipts)
    assert not receipts.exists()
