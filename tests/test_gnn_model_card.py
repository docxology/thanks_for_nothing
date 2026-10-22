# Copyright (c) 2026 Daniel Ari Friedman
import json
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.patches import Circle, FancyArrowPatch

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gnn_figures import draw_declaration_graph
from thanks_for_nothing.gnn_graphs import graph_model_path
from thanks_for_nothing.gnn_model_card import (
    gnn_model_card_valid,
    model_card_document,
    write_gnn_model_card,
)
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.specifications import load_model
from thanks_for_nothing.visual_style import figure


def test_compact_declaration_arrows_follow_source_directions_and_reject_overshrink(pipeline_case):
    model = model_card_document(pipeline_case.output).cards[0].graph
    outcomes = {}
    for margin in (18, 7):
        fig, axis = figure(3.588, 1.5515, automatic_layout=False)
        fig.axes[0].set_position((0, 0, 1, 1))
        try:
            draw_declaration_graph(axis, model, node_margin_points=margin)
            fig.canvas.draw()
            nodes = {
                patch.get_gid().removeprefix("gnn_node_"): np.asarray(patch.center)
                for patch in fig.axes[0].patches
                if isinstance(patch, Circle)
            }
            directions = []
            body_lengths = []
            for patch in fig.axes[0].patches:
                if not isinstance(patch, FancyArrowPatch):
                    continue
                source, target = patch.get_gid().removeprefix("gnn_edge_").split("_")
                vertices = patch.get_path().vertices
                directions.append(np.dot(vertices[2] - vertices[0], nodes[target] - nodes[source]))
                endpoints = fig.axes[0].transData.transform(vertices[[0, 2]])
                body_lengths.append(np.linalg.norm(endpoints[1] - endpoints[0]) * 72 / fig.dpi)
            assert min(directions) > 0
            outcomes[margin] = min(body_lengths)
        finally:
            plt.close(fig)
    minimum_legible_body_points = 12
    assert outcomes[18] < minimum_legible_body_points
    assert outcomes[7] > minimum_legible_body_points


def test_complete_model_cards_use_consumed_declarations_and_reduced_settings(pipeline_case, tmp_path):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    page = write_gnn_model_card(output)
    assert gnn_model_card_valid(output)
    record = json.loads((output / "frontmatter/gnn-model-card.json").read_text())
    catalog = json.loads((output / "data/gnn_graphs.json").read_text())
    assert [card["graph"] for card in record["cards"]] == catalog["models"]
    assert record["parser_sha256"] == catalog["parser_sha256"]
    assert record["renderer_sha256"] == catalog["renderer_sha256"]
    for card in record["cards"]:
        declaration = graph_model_path(output, card["graph"]["model_id"])
        model = load_model(card["graph"]["model_id"], declaration.parent)
        assert card["parameters"] == json.loads(model.parameters_json)
        assert card["tensors"] == model.tensors.model_dump(mode="json")
        assert card["declaration"] == declaration.read_text()
        assert card["graph"]["source_sha256"] == model.source_hash
    assert record["dependencies"]["generalized-notation-notation"]["origin"]["vcs_info"]["commit_id"]
    assert page.links
    assert all((output / path).is_file() for path in (page.pdf, page.png, page.svg))
    html = (output / "frontmatter/gnn-model-card.html").read_text()
    assert html.count('<section id="') == len(record["cards"])
    assert html.count("data:image/png;base64,") >= len(record["cards"])


@pytest.mark.parametrize("defect", ["role", "omitted_model", "shape", "source", "native_asset"])
def test_card_admission_rejects_repaired_catalogs_and_unconsumed_sources(
    pipeline_case,
    tmp_path,
    defect,
):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    path = output / "data/gnn_graphs.json"
    record = json.loads(path.read_text())
    if defect == "role":
        record["models"][0]["execution"] = "Native GNN / pymdp"
    elif defect == "omitted_model":
        record["models"].pop()
    elif defect == "shape":
        record["models"][0]["tensor_shapes"][0][1][0] += 1
    elif defect == "source":
        specification = output / "specifications/gratitude.gnn.md"
        specification.write_text(specification.read_text() + "\n")
        record["models"][1]["source_sha256"] = file_digest(specification)
    else:
        image = output / record["assets"][0]["path"]
        image.write_bytes(image.read_bytes() + b"altered")
    path.write_text(json.dumps(record))
    with pytest.raises(ContractError):
        model_card_document(output)


@pytest.mark.parametrize("defect", ["missing", "json", "html", "png", "metadata", "receipt"])
def test_card_gate_rejects_missing_altered_and_forged_products(pipeline_case, tmp_path, defect):
    output = tmp_path / "output"
    shutil.copytree(pipeline_case.output, output)
    assert not gnn_model_card_valid(output)
    page = write_gnn_model_card(output)
    assert gnn_model_card_valid(output)
    if defect == "missing":
        (output / page.pdf).unlink()
    elif defect in {"json", "html", "png"}:
        path = output / "frontmatter" / f"gnn-model-card.{defect}"
        path.write_bytes(path.read_bytes() + b"altered")
    else:
        path = output / "reports/gnn_model_card.json"
        record = json.loads(path.read_text())
        if defect == "metadata":
            record["artifact"]["links"] = []
        else:
            record = {}
        path.write_text(json.dumps(record))
    assert not gnn_model_card_valid(output)
