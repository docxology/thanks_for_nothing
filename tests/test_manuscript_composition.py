# Copyright (c) 2026 Daniel Ari Friedman
import json
from dataclasses import replace
from shutil import copytree
from zipfile import ZipFile

import numpy as np
import pytest

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_composition import compose_source
from thanks_for_nothing.manuscript_quantities import additional_variables
from thanks_for_nothing.manuscript_references import historical_variables, source_array_variables
from thanks_for_nothing.manuscript_variables import manuscript_variables, model_variables
from thanks_for_nothing.publication_checks import manuscript_variables_valid
from thanks_for_nothing.reporting import hydration


def test_reduced_real_design_drives_narrative_captions_and_tensor_bindings(pipeline_case):
    bundle = read_bundle(pipeline_case.output)
    values = manuscript_variables(bundle)
    assert len(values) == len({row.name for row in values})
    indexed = {row.name: row for row in values}
    assert indexed["AGENTS"].value == "2"
    assert indexed["STUDY_REPLICATES"].value == "2"
    assert indexed["GAZE_STEPS"].value == "8"
    assert indexed["BOUNDARY_REPLICATES"].value == "4"
    assert indexed["GAZE_CONTEXTS"].value == "2"
    assert indexed["JOINT_BLOCKS"].value == "3"
    text, ledger = compose_source(
        pipeline_case.root,
        pipeline_case.output,
        bundle,
        {row.token: row.text for row in hydration(bundle)},
    )
    assert "The corrected recall study contains 2 independent agent-world units" in text
    assert "1280 independent agent-world units" not in text
    assert "{{" not in text
    assert {row.path for row in ledger.templates} == {
        "docs/manuscript/manuscript.md",
        "docs/manuscript/supplement.md",
        "docs/manuscript/captions.yaml",
    }
    assert ledger.main_sections == (
        "Abstract",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
        "References",
    )
    assert manuscript_variables_valid(pipeline_case.root, pipeline_case.output)


@pytest.mark.parametrize(
    "target",
    ["value", "producer_hash", "composed_text", "supplement", "concept_source", "caption_source"],
)
def test_forged_values_and_stale_supplements_are_rejected(pipeline_case, tmp_path, target):
    root, output = tmp_path / "source", tmp_path / "output"
    copytree(pipeline_case.root / "docs", root / "docs")
    copytree(pipeline_case.root / "data", root / "data")
    copytree(pipeline_case.output, output)
    bundle = read_bundle(output)
    text, ledger = compose_source(root, output, bundle, {r.token: r.text for r in hydration(bundle)})
    (output / "reports/manuscript.md").write_text(text)
    write_record(output / "reports/manuscript_variables.json", ledger)
    assert manuscript_variables_valid(root, output)
    if target in {"value", "producer_hash"}:
        path = output / "reports/manuscript_variables.json"
        record = json.loads(path.read_text())
        row = next(r for r in record["variables"] if r["name"] == "AGENTS")
        row["value" if target == "value" else "source_sha256"] = "999" if target == "value" else "0" * 64
        path.write_text(json.dumps(record))
    elif target == "composed_text":
        path = output / "reports/manuscript.md"
        path.write_text(
            path.read_text().replace("2 independent agent-world", "999 independent agent-world", 1)
        )
    elif target == "concept_source":
        path = output / "data/concepts.json"
        definitions = json.loads(path.read_text())
        definitions[0]["name"] = "Unrecorded absence"
        path.write_text(json.dumps(definitions))
    elif target == "caption_source":
        path = root / "docs/manuscript/captions.yaml"
        path.write_text(
            path.read_text().replace("Different questions require", "Distinct questions require")
        )
    else:
        path = root / "docs/manuscript/supplement.md"
        path.write_text(path.read_text() + "\nChanged technical interpretation.\n")
    if target == "concept_source":
        with pytest.raises(ContractError, match="Concept vocabulary"):
            manuscript_variables_valid(root, output)
    else:
        assert not manuscript_variables_valid(root, output)


@pytest.mark.parametrize(
    "defect", ["missing_method", "duplicate_supplement", "unknown_token", "missing_supplement"]
)
def test_imrad_and_resolution_fail_closed(pipeline_case, tmp_path, defect):
    docs = tmp_path / "docs/manuscript"
    docs.mkdir(parents=True)
    text = (
        "\n\n".join(
            f"# {heading}"
            for heading in ("Abstract", "Introduction", "Methods", "Results", "Discussion", "References")
        )
        + "\n{{SUPPLEMENT}}\n"
    )
    supplement = docs / "supplement.md"
    supplement.write_text("## Supplemental methods\n{{AGENTS}}\n")
    if defect == "missing_method":
        text = text.replace("# Methods", "# Model")
    elif defect == "duplicate_supplement":
        text += "{{SUPPLEMENT}}"
    elif defect == "unknown_token":
        supplement.write_text("{{UNDECLARED_SCIENTIFIC_VALUE}}")
    elif defect == "missing_supplement":
        supplement.rename(docs / "retained-supplement.md")
    (docs / "manuscript.md").write_text(text)
    with pytest.raises((ContractError, FileNotFoundError)):
        compose_source(tmp_path, pipeline_case.output, read_bundle(pipeline_case.output), {})


def test_canonical_bundle_binding_is_independent_of_mapping_order(pipeline_case, tmp_path):
    docs = tmp_path / "docs/manuscript"
    docs.mkdir(parents=True)
    (docs / "manuscript.md").write_text("{{AGENTS}}")
    bundle = read_bundle(pipeline_case.output)
    reordered = replace(bundle, source=dict(reversed(tuple(bundle.source.items()))))
    _, first = compose_source(tmp_path, pipeline_case.output, bundle, {})
    _, second = compose_source(tmp_path, pipeline_case.output, reordered, {})
    assert first == second


def test_dimension_values_bind_executed_tensors_and_reject_changed_declaration(pipeline_case, tmp_path):
    output = tmp_path / "output"
    copytree(pipeline_case.output / "specifications", output / "specifications")
    bundle = read_bundle(pipeline_case.output)
    names = {"MODEL_RECALL_STATES", "MODEL_RECALL_OBSERVATIONS", "MODEL_ATTENTION_LOCATIONS"}
    values = additional_variables(output, bundle, names)
    assert {row.name: row.value for row in values} == {
        "MODEL_RECALL_STATES": "2",
        "MODEL_RECALL_OBSERVATIONS": "3",
        "MODEL_ATTENTION_LOCATIONS": "13",
    }
    path = output / "specifications/gratitude.gnn.md"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ContractError, match="Recall tensor declarations"):
        additional_variables(output, bundle, names)


def test_tensor_binding_rejects_a_normalized_but_different_real_model(pipeline_case, tmp_path):
    specifications = tmp_path / "specifications"
    copytree(pipeline_case.output / "specifications", specifications)
    path = specifications / "emptiness_practice.gnn.md"
    path.write_text(
        path.read_text().replace(
            "A=[[0.85,0.55,0.15],[0.15,0.45,0.85]]", "A=[[0.80,0.55,0.15],[0.20,0.45,0.85]]"
        )
    )
    with pytest.raises(ContractError, match="tensor"):
        model_variables(read_bundle(pipeline_case.output), specifications)


@pytest.mark.parametrize("defect", ["source_hash", "percentage", "source_bytes", "receipt_bytes"])
def test_historical_values_reject_missing_custody_and_invalid_transcriptions(
    pipeline_case, tmp_path, defect
):
    copytree(pipeline_case.root / "data", tmp_path / "data")
    values = historical_variables(tmp_path)
    indexed = {row.name: row.value for row in values}
    assert indexed["SOURCE_AFTER_POSITIVE"] == "90.1/6.1/3.8"
    assert indexed["DESTENO_PARTICIPANTS"] == "75"
    path = tmp_path / "data/sources/manuscript_observations.json"
    record = json.loads(path.read_text())
    if defect == "source_hash":
        record["gratitude_source_sha256"] = "0" * 64
    elif defect == "percentage":
        record["after_positive_profile_percent"][0] = 89.0
    elif defect == "source_bytes":
        with (tmp_path / "data/sources/gratitude_preprint_v1.docx").open("ab") as stream:
            _ = stream.write(b"altered")
    else:
        with (tmp_path / record["desteno_receipt"]).open("ab") as stream:
            _ = stream.write(b"altered")
    path.write_text(json.dumps(record))
    with pytest.raises(ContractError, match="Historical"):
        historical_variables(tmp_path)


@pytest.mark.parametrize("version", [(1, 0), (2, 0)])
def test_source_array_count_uses_actual_numeric_header(tmp_path, version):
    (tmp_path / "data").mkdir()
    with (
        ZipFile(tmp_path / "data/source_reconstruction.npz", "w") as archive,
        archive.open("baseline.npy", "w") as stream,
    ):
        np.lib.format.write_array(stream, np.ones((7, 2, 3, 4)), version=version, allow_pickle=False)
    assert source_array_variables(tmp_path)[0].value == "7"


@pytest.mark.parametrize("defect", ["rank", "empty", "objects", "version"])
def test_source_array_count_rejects_invalid_baseline_headers(tmp_path, defect):
    (tmp_path / "data").mkdir()
    shape = (7, 2) if defect == "rank" else ((0, 2, 3, 4) if defect == "empty" else (7, 2, 3, 4))
    array = np.ones(shape, dtype=object if defect == "objects" else float)
    with (
        ZipFile(tmp_path / "data/source_reconstruction.npz", "w") as archive,
        archive.open("baseline.npy", "w") as stream,
    ):
        np.lib.format.write_array(stream, array, version=(3, 0) if defect == "version" else (1, 0))
    with pytest.raises(ContractError, match="reconstruction"):
        source_array_variables(tmp_path)
