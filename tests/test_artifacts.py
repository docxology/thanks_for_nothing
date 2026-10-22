# Copyright (c) 2026 Daniel Ari Friedman
import json
from hashlib import sha256

from thanks_for_nothing.artifacts import Artifact, inventory, record_json, write_record


def test_dataclass_and_nested_source_mapping_serialize_as_values(tmp_path):
    artifact = Artifact("sample.txt", "abc", 7)
    source = {
        "source_sha256": "abc",
        "controls": {"pass": True, "values": [0.0, 1.0]},
        "scope": "bounded",
        "artifact": artifact,
    }
    path = tmp_path / "nested" / "record.json"

    write_record(path, source)

    assert json.loads(path.read_text()) == {
        "source_sha256": "abc",
        "controls": {"pass": True, "values": [0.0, 1.0]},
        "scope": "bounded",
        "artifact": {"path": "sample.txt", "sha256": "abc", "bytes": 7},
    }
    assert json.loads(record_json(artifact, record_type=Artifact))["bytes"] == 7
    assert path.read_bytes().endswith(b"\n")


def test_inventory_hash_changes_with_real_file_bytes(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("first")
    (tmp_path / "artifact_manifest.json").write_text("excluded")
    (tmp_path / "validation.json").write_text("excluded")
    (tmp_path / "subdir").mkdir()
    before = inventory(tmp_path)
    path.write_text("second")

    after = inventory(tmp_path)

    assert len(after.artifacts) == 1
    assert after.artifacts[0].sha256 == sha256(b"second").hexdigest()
    assert after.artifacts[0].bytes == len(b"second")
    assert after.artifacts[0].sha256 != before.artifacts[0].sha256
    assert after.artifacts[0].path == "data.json"
