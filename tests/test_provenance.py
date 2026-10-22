# Copyright (c) 2026 Daniel Ari Friedman
import hashlib
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from thanks_for_nothing.provenance import (
    DEPENDENCY_PINS,
    ProvenanceError,
    build_provenance_audit,
    executing_dependency,
)


@pytest.fixture
def source_copy(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "data/sources", tmp_path / "data/sources")
    return tmp_path


def test_actual_sources_and_executing_distributions_admit(source_copy):
    report = build_provenance_audit(source_copy)
    assert len(report.sources) == 4
    assert len(report.dependencies) == 2
    assert all(report.controls.values())
    assert {row.version for row in report.dependencies} == {"3.0.0", "4.1.0"}


def test_replacing_source_and_manifest_together_cannot_forge_original(source_copy):
    source = source_copy / "data/sources/gratitude_original.ipynb"
    source.write_text('{"nbformat":4,"cells":[]}')
    manifest = source_copy / "data/sources/source_manifest.json"
    data = json.loads(manifest.read_text())
    data["sources"][1]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    with pytest.raises(ProvenanceError, match="independent original digest"):
        build_provenance_audit(source_copy)


def test_missing_source_rejects(source_copy):
    path = source_copy / "data/sources/gratitude_preprint_v1.docx"
    path.rename(path.with_suffix(".absent"))
    with pytest.raises(ProvenanceError):
        build_provenance_audit(source_copy)


def test_duplicate_manifest_row_rejects(source_copy):
    path = source_copy / "data/sources/source_manifest.json"
    manifest = json.loads(path.read_text())
    manifest["sources"].append(manifest["sources"][0])
    path.write_text(json.dumps(manifest))
    with pytest.raises(ProvenanceError, match="inventory"):
        build_provenance_audit(source_copy)


@pytest.mark.parametrize(
    "change", [{"version": "0"}, {"commit": "0" * 40}, {"repository": "https://example.com/wrong"}]
)
def test_actual_dependency_cannot_satisfy_wrong_declared_identity(change):
    pin = replace(DEPENDENCY_PINS[0], **change)
    with pytest.raises(ProvenanceError, match="identity"):
        executing_dependency(pin)
