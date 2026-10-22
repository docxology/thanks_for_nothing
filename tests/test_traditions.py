# Copyright (c) 2026 Daniel Ari Friedman
import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.tradition_figures import world_traditions
from thanks_for_nothing.traditions import (
    TraditionSelection,
    TraditionsRecord,
    build_traditions,
    traditions_valid,
    write_traditions,
)
from thanks_for_nothing.traditions_html import render_traditions_html
from thanks_for_nothing.validation import validate_project

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def texts(tmp_path):
    shutil.copytree(ROOT / "data/scholarship", tmp_path / "data/scholarship")
    return tmp_path


def test_source_bound_rows_and_real_edit_replay(texts):
    output = texts / "output"
    record = write_traditions(texts, output)
    assert traditions_valid(texts, output)
    assert {s.key for s in record.sources} == {
        key for row in record.selection.rows for key in row.source_keys
    }
    assert all(file_digest(texts / item.path) == item.sha256 for item in record.inputs)
    path = texts / "data/scholarship/traditions.json"
    original = path.read_text()
    path.write_text(original.replace("Unfilled hollow", "Useful hollow"))
    assert not traditions_valid(texts, output)
    updated = write_traditions(texts, output)
    assert updated != record
    assert traditions_valid(texts, output)
    catalog = texts / "data/scholarship/sources.json"
    catalog.write_text(catalog.read_text().replace("Hukam and speech", "Divine command and speech"))
    assert not traditions_valid(texts, output)


@pytest.mark.parametrize("mutation", ["id", "source_keys", "unknown", "blank"])
def test_selection_rejects_ambiguous_or_empty_rows(texts, mutation):
    path = texts / "data/scholarship/traditions.json"
    payload = json.loads(path.read_text())
    if mutation == "id":
        payload["rows"][1]["id"] = payload["rows"][0]["id"]
    elif mutation == "source_keys":
        payload["rows"][0]["source_keys"] *= 2
    elif mutation == "unknown":
        payload["rows"][0]["wisdom_score"] = 1
    else:
        payload["rows"][0]["limit"] = " "
    with pytest.raises(ValidationError):
        TraditionSelection.model_validate(payload)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "http"])
def test_catalog_rejects_unresolved_or_unsafe_identity(texts, mutation):
    path = texts / "data/scholarship/sources.json"
    payload = json.loads(path.read_text())
    if mutation == "missing":
        payload["sources"] = [s for s in payload["sources"] if s["key"] != "khalsajapji2"]
    elif mutation == "duplicate":
        payload["sources"].append(payload["sources"][0])
    else:
        payload["sources"][0]["url"] = "http://example.org/"
    path.write_text(json.dumps(payload))
    with pytest.raises((ContractError, ValidationError)):
        build_traditions(texts)


def test_record_requires_exact_source_closure(texts):
    record = build_traditions(texts)
    payload = record.model_dump(mode="json")
    payload["sources"].pop()
    with pytest.raises(ValidationError, match="do not close"):
        TraditionsRecord.model_validate(payload)
    payload = record.model_dump(mode="json")
    payload["sources"].append(payload["sources"][0])
    with pytest.raises(ValidationError, match="do not close"):
        TraditionsRecord.model_validate(payload)


def test_real_figure_changes_with_authored_text(texts):
    output = texts / "output"
    record = write_traditions(texts, output)
    figure = world_traditions(output / "figures")
    assert figure.source_sha256 == (file_digest(output / "data/world_traditions.json"),)
    assert figure.publication_min_font_points >= 10.5
    path = texts / "data/scholarship/traditions.json"
    path.write_text(path.read_text().replace("Unfilled hollow", "Useful hollow"))
    updated = write_traditions(texts, output)
    changed = world_traditions(output / "figures")
    assert updated != record
    assert changed.svg_sha256 != figure.svg_sha256
    assert "Useful hollow" in (output / "figures/world_traditions.svg").read_text()


@pytest.mark.parametrize("mutation", ["long_word", "long_figure"])
def test_overfilled_figure_rejected(texts, mutation):
    output = texts / "output"
    record = write_traditions(texts, output)
    payload = record.model_dump(mode="json")
    if mutation == "long_word":
        payload["selection"]["rows"][0]["absence"] = "word " + "W" * 100
        message = "unbreakable"
    else:
        payload["selection"]["rows"][0]["absence"] = "long label " * 500
        message = "readable manuscript page"
    write_record(output / "data/world_traditions.json", TraditionsRecord.model_validate(payload))
    with pytest.raises(ContractError, match=message):
        world_traditions(output / "figures")


def test_companion_escapes_authored_text_and_preserves_sources(texts):
    record = build_traditions(texts)
    html = render_traditions_html(record)
    assert html.count("<article ") == len(record.selection.rows)
    assert html.count("<details>") == len(record.selection.rows)
    assert all(str(source.url).replace("&", "&amp;") in html for source in record.sources)
    assert 'role="status" aria-live="polite"' in html
    assert '<label for="search">' in html
    payload = record.model_dump(mode="json")
    payload["selection"]["rows"][0]["absence"] = '<script>alert("unsafe")</script>'
    escaped = render_traditions_html(TraditionsRecord.model_validate(payload))
    assert '<script>alert("unsafe")</script>' not in escaped
    assert "&lt;script&gt;alert(&quot;unsafe&quot;)&lt;/script&gt;" in escaped


def test_project_gate_rejects_changed_companion(pipeline_case, tmp_path):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    path = output / "world_traditions.html"
    path.write_text(path.read_text().replace("Refrain from unwanted imposition.", "Impose on others."))
    report = validate_project(
        pipeline_case.root,
        output,
        require_render=False,
        specification_dir=pipeline_case.specifications,
    )
    gates = {gate.name: gate.passed for gate in report.gates}
    assert not report.all_pass
    assert gates["world_traditions_provenance"] is False
