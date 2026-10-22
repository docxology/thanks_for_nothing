# Copyright (c) 2026 Daniel Ari Friedman
import json
import shutil
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from gnn.parsers.markdown_parser import MarkdownGNNParser

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_design import load_gaze_task
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.specifications import Tensors, load_model
from thanks_for_nothing.standalone_gnn import (
    ModelContext,
    conditional_channels,
    conditional_model,
    generative_run,
    read_generative_catalog,
    standalone_model,
)


def test_real_gnn_joint_query_dynamics_match_independent_conditional_predictions(tmp_path):
    task = load_gaze_task()
    with generative_run(tmp_path) as run:
        model = conditional_model(
            "scene_open",
            task.channels,
            task.open_prior,
            np.asarray(task.model.tensors.C),
            context=ModelContext(
                (task.model,),
                "thanks_for_nothing.gaze_active:run_gaze_episode",
                "Query-major candidate-minor controlled model.",
                initial_query=1,
            ),
        )
    path = tmp_path / next(iter(run.models.values())).source_path
    assert path.read_text() == model.source_text
    parsed = MarkdownGNNParser().parse_string(path.read_text())
    assert parsed.success
    assert not parsed.errors
    assert not parsed.warnings
    assert load_model(model.model_id, path.parent) == model
    assert np.allclose(conditional_channels(model, len(task.channels)), task.channels, atol=1e-15)
    prior = np.asarray([0.2, 0.3, 0.5])
    initial = np.zeros(len(model.tensors.D))
    initial[: len(prior)] = prior
    for query, channel in enumerate(task.channels):
        next_state = np.asarray(model.tensors.B)[:, :, query] @ initial
        assert np.allclose(np.asarray(model.tensors.A) @ next_state, channel @ prior, atol=1e-15)
    assert "q[" in model.source_text
    assert "z[" in model.source_text
    declared_initial = np.asarray(model.tensors.D).reshape(len(task.channels), -1)
    assert np.allclose(declared_initial[1], task.open_prior)
    assert np.count_nonzero(np.sum(declared_initial, axis=1)) == 1


def test_standalone_admission_rejects_unknown_families_and_bad_shapes():
    model = load_model("gratitude")
    context = ModelContext((model,), "thanks_for_nothing.experiments:sample_world", "Test law")
    with pytest.raises(ContractError, match="Unknown"):
        standalone_model("unknown", model.tensors, context=context)
    with pytest.raises(ContractError, match="shape"):
        conditional_model("scene_open", np.ones((2, 3)), np.ones(3), np.ones(3), context=context)
    with pytest.raises(ContractError, match="Initial GNN query"):
        conditional_model(
            "scene_open",
            np.ones((2, 1, 3)),
            np.ones(3) / 3,
            np.zeros(1),
            context=replace(context, initial_query=2),
        )
    invalid = Tensors.model_validate(
        {
            "A": [[-1.0, 2.0], [2.0, -1.0]],
            "B": [[[1.0], [0.0]], [[0.0], [1.0]]],
            "C": [0.0, 0.0],
            "D": [0.5, 0.5],
        }
    )
    with pytest.raises((ContractError, ValueError)):
        standalone_model("optimism_well", invalid, context=context)


def test_execution_scope_rejects_missing_coverage_nested_scopes_and_changed_bytes(tmp_path):
    model = load_model("gratitude")
    context = ModelContext((model,), "thanks_for_nothing.experiments:sample_world", "Test law")
    with generative_run(tmp_path) as run:
        with pytest.raises(ContractError, match="already active"), generative_run(tmp_path):
            pass
        standalone_model("recall_world", model.tensors, context=context)
        standalone_model("recall_world", model.tensors, context=context)
        record = next(iter(run.models.values()))
        assert record.uses == 2
        (tmp_path / record.source_path).write_text("changed")
        with pytest.raises(ContractError, match="changed execution"):
            standalone_model("recall_world", model.tensors, context=context)
    with pytest.raises(ContractError, match="coverage"):
        run.write()
    with generative_run(tmp_path / "origins"):
        standalone_model("recall_world", model.tensors, context=context)
        forged = replace(model, source_text="changed")
        with pytest.raises(ContractError, match="origin collision"):
            standalone_model("recall_world", model.tensors, context=replace(context, origins=(forged,)))


def test_complete_scientific_execution_preserves_every_gnn_instance_and_origin(pipeline_case):
    output = pipeline_case.output
    catalog = read_generative_catalog(output)
    assert all(m.uses > 0 for m in catalog.models)
    assert len(catalog.models) > 13
    assert any(len(m.origins) > 1 for m in catalog.models)
    for record in catalog.models:
        path = output / record.source_path
        model = load_model(record.model_id, path.parent)
        assert model.source_hash == file_digest(path)
        assert record.evidence_sha256 == file_digest(output / record.evidence_artifact)
    boundary = next(m for m in catalog.models if m.family == "boundary_diagnostic")
    model = load_model(boundary.model_id, (output / boundary.source_path).parent)
    assert len(model.tensors.D) > len(load_model("boundary_gaze").tensors.D)
    assert len(model.tensors.B[0][0]) > 1
    assert "B={" in model.source_text


@pytest.mark.parametrize(
    "defect", ["family", "duplicate", "source_run", "uses", "evidence", "source", "origin", "namespace"]
)
def test_gnn_execution_catalog_rejects_forged_coverage_and_repaired_hashes(
    pipeline_case, tmp_path, defect
):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    path = output / "data/generative_models.json"
    record = json.loads(path.read_text())
    row = record["models"][0]
    if defect == "family":
        record["models"] = [m for m in record["models"] if m["family"] != row["family"]]
    elif defect == "duplicate":
        record["models"].append(row.copy())
    elif defect == "source_run":
        record["source_tree_sha256"] = "0" * 64
    elif defect == "uses":
        row["uses"] = 0
    elif defect == "evidence":
        row["evidence_sha256"] = "0" * 64
    elif defect == "source":
        source = output / row["source_path"]
        source.write_text(
            source.read_text().replace("## ModelAnnotation\n", "## ModelAnnotation\nChanged ")
        )
        row["source_sha256"] = file_digest(source)
    elif defect == "origin":
        name, digest = row["origins"][0]
        source = output / "specifications/origins" / f"{name}_{digest}.gnn.md"
        source.write_text(source.read_text() + "\n")
    else:
        row["model_id"] = "../escaped"
    path.write_text(json.dumps(record))
    with pytest.raises((ContractError, ValueError, OSError)):
        read_generative_catalog(output)


def test_changed_gnn_region_changes_complete_model_and_consumed_channel(tmp_path):
    source = Path(__file__).resolve().parents[1] / "src/thanks_for_nothing/models"
    chosen = tmp_path / "models"
    shutil.copytree(source, chosen)
    before = load_gaze_task(chosen)
    path = chosen / "gaze.gnn.md"
    text = path.read_text()
    line = next(row for row in text.splitlines() if row.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"]["channels"][1][0][0] += 0.02
    settings[0]["parameters"]["channels"][1][2][0] -= 0.02
    path.write_text(text.replace(line, "settings=" + json.dumps(settings)))
    after = load_gaze_task(chosen)
    assert not np.array_equal(before.channels, after.channels)
    assert np.array_equal(before.channels[0], after.channels[0])
    assert not np.allclose(before.channels[1] @ before.open_prior, after.channels[1] @ after.open_prior)
