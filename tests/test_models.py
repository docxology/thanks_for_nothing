# Copyright (c) 2026 Daniel Ari Friedman
"""Actual GNN edits must affect numbers or fail before simulation."""

import pytest
from pydantic import ValidationError

from tests.support.models import copy_models
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.specifications import load_model, load_study


def test_real_parser_and_hash_bound_model():
    model, design = load_study()
    assert model.tensors.A[0] == (0.7, 0.2)
    assert design.replicates > 1
    assert len(model.source_hash) == 64
    for name in ("nothingness", "attention_positive", "attention_negative"):
        assert load_model(name).source_hash


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("A[3,2,type=float]", "A[2,3,type=float]"),
        ("A=[[0.7,0.2],[0.1,0.1],[0.2,0.7]]", "A=[[1.7,0.2],[-0.9,0.1],[0.2,0.7]]"),
        ("D=[0.5,0.5]", "D=[0.8,0.8]"),
        ("## Connections", "## Unknown"),
        ('"recall_precision":4', '"recall_precision":0'),
        ('"luckiness":[0.1,0.3,0.5,0.7,0.9]', '"luckiness":[]'),
        ('"luckiness":[0.1,0.3,0.5,0.7,0.9]', '"luckiness":[0.1,0.1]'),
        ('"optimism_well":[[0.6,0.2],[0.4,0.8]]', '"optimism_well":[[0.6,0.2],[0.8,0.8]]'),
    ],
)
def test_real_invalid_source_fails(tmp_path, old, new):
    copy_models(tmp_path)
    path = tmp_path / "gratitude.gnn.md"
    original = path.read_text()
    assert old in original
    path.write_text(original.replace(old, new))
    with pytest.raises((ValueError, ValidationError, ContractError)):
        load_study(tmp_path)


def test_missing_file_is_fatal(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_study(tmp_path)


def test_invalid_task_prior_bounds(tmp_path):
    copy_models(tmp_path)
    path = tmp_path / "gratitude.gnn.md"
    path.write_text(path.read_text().replace('"task_prior_min":0.05', '"task_prior_min":0.99'))
    with pytest.raises(ContractError, match="bounds"):
        load_study(tmp_path)


def test_valid_wrong_model_dimensions_rejected(tmp_path):
    copy_models(tmp_path)
    path = tmp_path / "gratitude.gnn.md"
    original = path.read_text()
    replacement = (tmp_path / "attention_positive.gnn.md").read_text()
    settings = original.split("settings=")[1]
    path.write_text(
        replacement.split("settings=")[0].replace("attention_positive", "gratitude")
        + "settings="
        + settings
    )
    with pytest.raises(ContractError, match="three observations"):
        load_study(tmp_path)
