# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from shutil import copy2, copytree
from typing import Literal, assert_never
from xml.etree import ElementTree as ET

import pytest
from defusedxml.ElementTree import fromstring
from pydantic import TypeAdapter

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.figure_checks import figures_valid, legend_valid
from thanks_for_nothing.figure_placement import figure_placement_valid
from thanks_for_nothing.visual_style import FigureRecord, figure, save


def test_figure_export_retains_a_visible_key_when_its_title_wraps(tmp_path):
    write_record(tmp_path / "data/source.json", {"values": [0, 1]})
    fig, axis = figure()
    _ = axis.plot([0, 1], [0, 1], color="#007C83", label="Measured fixture")
    _ = axis.set(title="A long scientific title whose complete description needs more than one line")

    record = save(
        fig, tmp_path / "figures", "learning_trajectories", "Fixture", "Fixture", ("data/source.json",)
    )

    assert legend_valid(
        (tmp_path / "figures/learning_trajectories.svg").read_text(), record.legend_labels
    )


@pytest.mark.parametrize("defect", ["undeclared", "clipped", "wide_key"])
def test_figure_export_rejects_an_unreadable_or_undeclared_key(
    tmp_path, defect: Literal["undeclared", "clipped", "wide_key"]
):
    write_record(tmp_path / "data/source.json", {"values": [0, 1]})
    fig, axis = figure()
    name, label = "learning_trajectories", "Fixture"
    match defect:
        case "undeclared":
            name = "undeclared"
        case "clipped":
            _ = axis.axis("off")
            _ = axis.text(3, 3, "Outside the export", fontsize=11)
        case "wide_key":
            label = "W" * 64
        case _:
            assert_never(defect)
    _ = axis.plot([0, 1], [0, 1], color="#007C83", label=label)

    with pytest.raises(ContractError, match=r"legend|boundary"):
        save(fig, tmp_path / "figures", name, "Fixture", "Fixture", ("data/source.json",))

    assert not (tmp_path / "figures" / f"{name}.png").exists()


@pytest.mark.parametrize("defect", ["untouched", "removed_key", "wrong_label", "rogue_color"])
def test_figure_gate_checks_vector_encodings_even_when_hashes_are_repaired(
    pipeline_case, tmp_path, defect: Literal["untouched", "removed_key", "wrong_label", "rogue_color"]
):
    output = tmp_path / "tampered-figures"
    copytree(pipeline_case.output, output)
    path = output / "reports/figure_source_map.json"
    records = TypeAdapter(tuple[FigureRecord, ...]).validate_json(path.read_text())
    record = records[0]
    vector = output / f"figures/{record.name}.svg"
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    tree = fromstring(vector.read_text())
    key = next(node for node in tree.iter() if node.get("id") == "legend_figure_key")
    match defect:
        case "untouched":
            pass
        case "removed_key":
            parent = next(node for node in tree.iter() if key in list(node))
            parent.remove(key)
        case "wrong_label":
            label = next(node for node in key.iter() if node.get("id") == "key_label_0")
            text = next(node for node in label.iter() if node.tag.endswith("}text"))
            text.text = "Incorrect encoding"
        case "rogue_color":
            node = next(node for node in tree.iter() if "#142e3a" in node.get("style", ""))
            node.set("style", node.get("style", "").replace("#142e3a", "#ff00ff", 1))
        case _:
            assert_never(defect)
    data = ET.tostring(tree, encoding="unicode")
    vector.write_text(data)
    write_record(
        path, (replace(record, svg_sha256=sha256(vector.read_bytes()).hexdigest()), *records[1:])
    )

    accepted = figures_valid(output)

    assert accepted is (defect == "untouched")


@pytest.mark.parametrize(
    "svg",
    [
        "<svg>",
        '<!DOCTYPE svg [<!ENTITY trap "expanded">]><svg>&trap;</svg>',
    ],
)
def test_legend_reader_rejects_malformed_or_entity_bearing_xml(svg):
    assert not legend_valid(svg, ("Fixture",))


@pytest.mark.parametrize(
    "defect", ["untouched", "body_chart", "missing_situation", "missing_supplement"]
)
def test_manuscript_placement_requires_context_and_preserves_complete_detail(
    tmp_path, defect: Literal["untouched", "body_chart", "missing_situation", "missing_supplement"]
):
    source = Path(__file__).resolve().parents[1] / "docs/manuscript"
    target = tmp_path / "docs/manuscript"
    target.mkdir(parents=True)
    for name in ("manuscript.md", "supplement.md"):
        copy2(source / name, target / name)
    main_path, supplement_path = target / "manuscript.md", target / "supplement.md"
    main, supplement = main_path.read_text(), supplement_path.read_text()
    match defect:
        case "untouched":
            pass
        case "body_chart":
            line = next(
                line for line in supplement.splitlines() if "figures/paired_contrasts.png" in line
            )
            main = main.replace(
                "# Results {#sec-main-results}", "# Results {#sec-main-results}\n\n" + line
            )
        case "missing_situation":
            main = "\n".join(
                line for line in main.splitlines() if "figures/recall_situation.png" not in line
            )
        case "missing_supplement":
            supplement = "\n".join(
                line for line in supplement.splitlines() if "figures/paired_contrasts.png" not in line
            )
        case _:
            assert_never(defect)
    main_path.write_text(main)
    supplement_path.write_text(supplement)

    accepted = figure_placement_valid(tmp_path)

    assert accepted is (defect == "untouched")
