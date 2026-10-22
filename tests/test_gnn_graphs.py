# Copyright (c) 2026 Daniel Ari Friedman
"""Reject stale, missing and forged products of actual GNN rendering."""

import json
import shutil
from dataclasses import replace

import pytest
from PIL import Image
from pydantic import TypeAdapter

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gnn_figures import gnn_model_graph, gnn_model_tensors
from thanks_for_nothing.gnn_graphs import describe_model, gnn_graphs_valid
from thanks_for_nothing.provenance import file_digest


def test_native_graphs_bind_all_declarations(pipeline_case):
    output = pipeline_case.output
    bundle = read_bundle(output)
    assert gnn_graphs_valid(output, bundle)
    record = json.loads((output / "data/gnn_graphs.json").read_text())
    assert {m["model_id"] for m in record["models"]} == {
        p.name.removesuffix(".gnn.md")
        for p in (output / "specifications").rglob("*.gnn.md")
        if "origins" not in p.parts
    }
    for model in record["models"]:
        assert model["edges"]
        assert model["tensor_shapes"]
        assert model["evidence_sha256"] == file_digest(output / model["evidence_artifact"])
        image = output / "gnn" / model["model_id"] / f"{model['model_id']}_network_graph.png"
        assert image.stat().st_size > 1000


@pytest.mark.parametrize("defect", ["edge", "dimensions", "source", "consumer", "renderer", "schema"])
def test_forged_graph_record_rejected(pipeline_case, tmp_path, defect):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    path = output / "data/gnn_graphs.json"
    record = json.loads(path.read_text())
    if defect == "edge":
        record["models"][0]["edges"].pop()
    elif defect == "dimensions":
        record["models"][0]["tensor_shapes"][0][1][0] += 1
    elif defect == "source":
        record["models"][0]["source_sha256"] = "0" * 64
    elif defect == "consumer":
        record["models"][0]["execution"] = "Native GNN / pymdp"
    elif defect == "renderer":
        record["renderer_sha256"] = "0" * 64
    else:
        record["schema"] = "forged"
    write_record(path, record)
    assert not gnn_graphs_valid(output, read_bundle(output))


@pytest.mark.parametrize(
    "defect",
    [
        "missing_image",
        "image_bytes",
        "stats_repaired_hash",
        "blank_repaired_hash",
        "wrong_model_repaired_hash",
        "orientation_repaired_hash",
    ],
)
def test_native_graph_product_defects_rejected(pipeline_case, tmp_path, defect):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    catalog = output / "data/gnn_graphs.json"
    record = json.loads(catalog.read_text())
    image = output / record["assets"][0]["path"]
    stats = output / record["assets"][1]["path"]
    if defect == "missing_image":
        image.rename(image.with_suffix(".preserved"))
    elif defect == "image_bytes":
        image.write_bytes(image.read_bytes() + b"mutated")
    elif defect in {"blank_repaired_hash", "wrong_model_repaired_hash"}:
        if defect == "blank_repaired_hash":
            Image.new("RGB", (640, 480), "white").save(image)
        else:
            shutil.copyfile(output / record["assets"][2]["path"], image)
        record["assets"][0]["sha256"] = file_digest(image)
        write_record(catalog, record)
    else:
        values = json.loads(stats.read_text())
        if defect == "orientation_repaired_hash":
            values["gnn_edge_orientation"] = {
                "directed_variable_pairs": 0,
                "undirected_variable_pairs": 999,
            }
        else:
            values["connection_types"] = {}
        write_record(stats, values)
        record["assets"][1]["sha256"] = file_digest(stats)
        write_record(catalog, record)
    assert not gnn_graphs_valid(output, read_bundle(output))


def test_real_graph_edit_updates_topology_and_figure(pipeline_case, tmp_path):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    bundle = read_bundle(output)
    model = describe_model(output, bundle, "gratitude")
    path = output / "specifications/gratitude.gnn.md"
    path.write_text(path.read_text().replace("D>s", "D>s\nD>A"))
    with pytest.raises(ContractError, match="executed model"):
        describe_model(output, bundle, "gratitude")
    bundle = replace(bundle, study=replace(bundle.study, model_sha256=file_digest(path)))
    changed = describe_model(output, bundle, "gratitude")
    assert len(changed.edges) == len(model.edges) + 1
    assert any(e.source == "D" and e.target == "A" for e in changed.edges)
    catalog = output / "data/gnn_graphs.json"
    record = json.loads(catalog.read_text())
    index = next(i for i, m in enumerate(record["models"]) if m["model_id"] == "gratitude")
    record["models"][index] = json.loads(TypeAdapter(type(changed)).dump_json(changed))
    write_record(catalog, record)
    graph = gnn_model_graph(output / "figures")
    tensors = gnn_model_tensors(output / "figures")
    svg = (output / "figures/gnn_model_graph.svg").read_text()
    assert "gnn_edge_D_A" in svg
    assert graph.source_sha256 == (file_digest(catalog),)
    assert tensors.source_sha256 == (file_digest(catalog),)
