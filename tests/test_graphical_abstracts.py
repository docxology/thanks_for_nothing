# Copyright (c) 2026 Daniel Ari Friedman
import json
import shutil
import subprocess

import pytest
from defusedxml import ElementTree
from pydantic import ValidationError

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.graphical_abstracts import (
    abstract_pages,
    graphical_abstracts_valid,
    write_graphical_abstracts,
)
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.publication_checks import publication_valid
from thanks_for_nothing.reporting import render_manuscript


def test_real_abstract_pages_resolve_reduced_design_and_precede_contents(pipeline_case, tmp_path):
    source = pipeline_case.output
    shutil.copytree(source, tmp_path / "output")
    output = tmp_path / "output"
    pages = abstract_pages(pipeline_case.root, output)
    ledger = json.loads((output / "reports/manuscript_variables.json").read_text())
    agents = next(row["value"] for row in ledger["variables"] if row["name"] == "AGENTS")
    assert f"Recall cohort: {agents} independent" in pages[1].subtitle
    assert "{{" not in pages[1].subtitle
    render_manuscript(pipeline_case.root, output, output / "reports/manuscript.md")
    assert graphical_abstracts_valid(pipeline_case.root, output)
    assert publication_valid(pipeline_case.root, output, require_render=True)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and real temporary PDF.
        [shutil.which("pdftotext") or "pdftotext", str(output / "manuscript.pdf"), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    rendered = result.stdout.split("\f")
    assert "What can" in rendered[1]
    assert "CONCEPTUAL GRAPHICAL ABSTRACT" in rendered[1]
    assert "From mechanisms to bounded claims" in rendered[2]
    assert "GNN / BAYESIAN MODEL CARD" in rendered[3]
    assert "Contents" in rendered[4]
    assert "Contents" not in rendered[1] + rendered[2] + rendered[3]
    links = subprocess.run(  # noqa: S603 - Fixed Poppler executable and the just-rendered PDF.
        [
            shutil.which("pdftohtml") or "pdftohtml",
            "-f",
            "2",
            "-l",
            "4",
            "-xml",
            "-i",
            "-stdout",
            str(output / "manuscript.pdf"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Bad named destination" not in links.stderr
    assert "failed to look up" not in links.stderr
    extracted = ElementTree.fromstring(links.stdout).findall("page")
    assert [len(page.findall(".//a")) for page in extracted] == [4, 6, 4]
    assert any(
        "frontmatter/gnn-model-card.html" in a.attrib["href"] for a in extracted[2].findall(".//a")
    )
    manifest = output / "reports/graphical_abstracts.json"
    clean = manifest.read_text()
    record = json.loads(clean)
    record["pages"].reverse()
    manifest.write_text(json.dumps(record))
    assert not graphical_abstracts_valid(pipeline_case.root, output)
    manifest.write_text(clean)
    image = output / record["pages"][0]["png"]
    image.write_bytes(image.read_bytes() + b"changed")
    assert not graphical_abstracts_valid(pipeline_case.root, output)


@pytest.mark.parametrize("defect", ["literal", "unknown", "missing_target", "duplicate", "empty"])
def test_abstract_declarations_reject_stale_values_and_invalid_structure(
    pipeline_case,
    tmp_path,
    defect,
):
    shutil.copytree(pipeline_case.root / "docs/manuscript", tmp_path / "docs/manuscript")
    path = tmp_path / "docs/manuscript/graphical-abstracts.yaml"
    text = path.read_text()
    if defect == "literal":
        text = text.replace("{{AGENTS}}", "4321")
    elif defect == "unknown":
        text = text.replace("{{AGENTS}}", "{{UNKNOWN_COHORT}}")
    elif defect == "missing_target":
        text = text.replace("sec-absence-model", "sec-absent-target")
    elif defect == "duplicate":
        text = text.replace("key: experiments", "key: meanings")
    else:
        text = "pages: []"
    path.write_text(text)
    with pytest.raises((ContractError, ValidationError)):
        abstract_pages(tmp_path, pipeline_case.output)


def test_abstract_manifest_requires_images_and_current_source(pipeline_case, tmp_path):
    shutil.copytree(pipeline_case.root / "docs/manuscript", tmp_path / "docs/manuscript")
    shutil.copytree(pipeline_case.output / "reports", tmp_path / "output/reports")
    shutil.copytree(pipeline_case.output / "data", tmp_path / "output/data")
    output = tmp_path / "output"
    assert not graphical_abstracts_valid(tmp_path, output)
    pages = write_graphical_abstracts(tmp_path, output)
    assert graphical_abstracts_valid(tmp_path, output)
    path = tmp_path / "docs/manuscript/graphical-abstracts.yaml"
    path.write_text(path.read_text().replace("What can", "How can"))
    assert not graphical_abstracts_valid(tmp_path, output)
    path.write_text(path.read_text().replace("How can", "What can"))
    (output / pages[0].pdf).unlink()
    assert not graphical_abstracts_valid(tmp_path, output)
    (output / "reports/graphical_abstracts.json").write_text("{}")
    assert not graphical_abstracts_valid(tmp_path, output)


def test_publication_build_receipt_binds_actual_products_and_execution_scope(pipeline_case):
    output = pipeline_case.output
    receipt = json.loads((output / "reports/publication_build.json").read_text())
    assert receipt["status"] == "complete"
    assert receipt["rendered"] is False
    assert receipt["notebook_execution"] == "not_reexecuted"
    assert receipt["numerical_source_receipt_sha256"] == file_digest(output / "data/source_tree.json")
    assert receipt["products"]
    assert all(file_digest(output / path) == digest for path, digest in receipt["products"].items())
