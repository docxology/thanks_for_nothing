# Copyright (c) 2026 Daniel Ari Friedman
import re
from dataclasses import replace
from hashlib import sha256
from shutil import copyfile, copytree

import pytest
from PIL import Image
from pydantic import TypeAdapter

from tests.support.models import small_model_directory
from thanks_for_nothing.artifact_checks import figures_valid
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.attention import build_attention_audit
from thanks_for_nothing.calibration import build_calibration_audit
from thanks_for_nothing.concepts import CONCEPTS
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.experiments import run_study
from thanks_for_nothing.figures import concept_map, generate_figures
from thanks_for_nothing.nothingness import build_nothingness_audit
from thanks_for_nothing.sensitivity import build_sensitivity_audit
from thanks_for_nothing.statistics import build_statistical_report
from thanks_for_nothing.visual_style import FigureRecord, figure, save


def test_real_figures_bind_sources_and_render_readable_content(tmp_path):
    models = small_model_directory(tmp_path)
    study = run_study(specification_dir=models)
    report = build_statistical_report(
        study.rows, seed=study.design.seed, bootstrap_draws=63, permutation_draws=63
    )
    absence = build_nothingness_audit(specification_dir=models)
    attention = build_attention_audit(specification_dir=models, output_dir=tmp_path / "native")
    grid = build_sensitivity_audit(study.design, specification_dir=models)
    calibration = build_calibration_audit(study.design)
    output = tmp_path / "output"
    for name, record in (
        ("study", study),
        ("statistics", report),
        ("nothingness", absence),
        ("attention", attention),
        ("sensitivity", grid),
        ("statistical_calibration", calibration),
        ("concepts", CONCEPTS),
    ):
        write_record(output / "data" / f"{name}.json", record)

    figures = generate_figures(study, report, absence, attention, grid, calibration, output / "figures")

    assert {record.name for record in figures} == {
        "concept_map",
        "learning_trajectories",
        "calibration_by_world",
        "paired_contrasts",
        "paired_spread",
        "weighting_sensitivity",
        "appreciation_null",
        "absence_information",
        "attention_policies",
        "sensitivity",
        "statistical_calibration",
    }
    for record in figures:
        png = output / "figures" / f"{record.name}.png"
        svg = output / "figures" / f"{record.name}.svg"
        assert sha256(png.read_bytes()).hexdigest() == record.png_sha256
        assert sha256(svg.read_bytes()).hexdigest() == record.svg_sha256
        assert record.source_sha256 == tuple(
            sha256((output / source).read_bytes()).hexdigest() for source in record.source_artifacts
        )
        assert record.min_font_points >= 9.5
        assert record.publication_min_font_points >= 9.5
        assert record.publication_min_font_points == pytest.approx(
            record.min_font_points * min(1.0, 6.54 / record.width_inches)
        )
        with Image.open(png) as image:
            image.load()
            assert image.width > 1000
            assert image.height > 600
            assert image.convert("L").getextrema()[0] < 200
        vector = svg.read_text()
        assert "<text" in vector
        assert "<svg" in vector
        assert 'id="legend_' in vector
        font_sizes = [float(value) for value in re.findall(r"font-size: ([\d.]+)px", vector)]
        assert font_sizes
        assert min(font_sizes) >= 9.5
        assert min(font_sizes) * min(1.0, 6.54 / record.width_inches) >= 9.5
    write_record(output / "figure_records.json", figures)


def test_source_hash_changes_without_changing_deterministic_figure_bytes(tmp_path):
    output = tmp_path / "figures"
    write_record(tmp_path / "data/nothingness.json", {"version": 1})
    write_record(tmp_path / "data/study.json", {"version": 1})
    write_record(tmp_path / "data/concepts.json", CONCEPTS)
    before = concept_map(output)
    write_record(tmp_path / "data/nothingness.json", {"version": 2})

    after = concept_map(output)

    assert before.source_sha256 != after.source_sha256
    assert before.png_sha256 == after.png_sha256
    assert before.svg_sha256 == after.svg_sha256


def test_figure_inventory_rejects_unknown_view_even_with_valid_image_and_source_hashes(
    pipeline_case, tmp_path
):
    output = tmp_path / "renamed-output"
    copytree(pipeline_case.output, output)
    path = output / "reports/figure_source_map.json"
    records = TypeAdapter(tuple[FigureRecord, ...]).validate_json(path.read_text())
    first = records[0]
    for suffix in ("png", "svg"):
        copyfile(output / f"figures/{first.name}.{suffix}", output / f"figures/unknown.{suffix}")
    write_record(path, (replace(first, name="unknown"), *records[1:]))

    assert not figures_valid(output)


def test_tiny_font_is_rejected_before_export(tmp_path):
    write_record(tmp_path / "data/source.json", {"value": 1})
    fig, ax = figure()
    _ = ax.text(0.5, 0.5, "Too small", fontsize=8)

    with pytest.raises(ContractError, match=r"at least 9\.5"):
        save(fig, tmp_path / "figures", "tiny", "Tiny", "Test", ("data/source.json",))

    assert not (tmp_path / "figures/tiny.png").exists()


def test_missing_source_is_rejected_before_export(tmp_path):
    fig, _ = figure()

    with pytest.raises(FileNotFoundError):
        save(fig, tmp_path / "figures", "missing", "Missing", "Test", ("data/missing.json",))

    assert not (tmp_path / "figures/missing.png").exists()


@pytest.mark.parametrize("sources", [(), ("data/empty.json",)])
def test_empty_source_binding_is_rejected_before_export(tmp_path, sources):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/empty.json").write_text("")
    fig, _ = figure()

    with pytest.raises(ContractError, match="contain data"):
        save(fig, tmp_path / "figures", "empty", "Empty", "Test", sources)

    assert not (tmp_path / "figures/empty.png").exists()
