# Copyright (c) 2026 Daniel Ari Friedman
import json
from hashlib import sha256

import pytest
from pydantic import ValidationError

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.external_inputs import acquire_external_inputs


def inventory(tmp_path, paths):
    manifest = tmp_path / "inputs.json"
    manifest.write_text(json.dumps({
        "schema": "thanks_for_nothing.external_inputs.v1",
        "inputs": [{"path": path, "sha256": sha256(b"original").hexdigest(),
                    "url": "https://example.org/source"} for path in paths],
    }))
    return manifest


def test_reuses_exact_inputs_without_changing_bytes(tmp_path):
    target = tmp_path / "input"
    target.write_bytes(b"original")
    before = target.stat().st_mtime_ns
    assert acquire_external_inputs(tmp_path, inventory(tmp_path, ["input"])) == (target,)
    assert target.stat().st_mtime_ns == before


@pytest.mark.parametrize("kind", ["wrong", "directory"])
def test_preserves_existing_mismatch(tmp_path, kind):
    target = tmp_path / "input"
    if kind == "wrong":
        target.write_bytes(b"changed")
    else:
        target.mkdir()
    with pytest.raises(ContractError, match="preserved without replacement"):
        acquire_external_inputs(tmp_path, inventory(tmp_path, ["input"]))
    assert target.read_bytes() == b"changed" if kind == "wrong" else target.is_dir()


@pytest.mark.parametrize("paths", [["../outside"], ["/outside"], ["same", "same"]])
def test_preflight_rejects_unsafe_inventory_before_writes(tmp_path, paths):
    with pytest.raises(ContractError, match="unsafe or duplicated"):
        acquire_external_inputs(tmp_path, inventory(tmp_path, paths))
    assert not (tmp_path / "same").exists()


def test_rejects_dangling_symlink(tmp_path):
    (tmp_path / "input").symlink_to(tmp_path / "missing")
    with pytest.raises(ContractError, match="unsafe"):
        acquire_external_inputs(tmp_path, inventory(tmp_path, ["input"]))
    assert (tmp_path / "input").is_symlink()


def test_rejects_non_https_manifest(tmp_path):
    manifest = inventory(tmp_path, ["input"])
    manifest.write_text(manifest.read_text().replace("https://", "http://"))
    with pytest.raises(ValidationError):
        acquire_external_inputs(tmp_path, manifest)
