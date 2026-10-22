# Copyright (c) 2026 Daniel Ari Friedman
"""Real admitted small-study pipeline fixture shared by artifact-boundary tests."""

import shutil

import numpy as np
import pytest

from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.pipeline import run_pipeline
from thanks_for_nothing.reanalysis import reanalyze
from thanks_for_nothing.validation import validate_project
from thanks_for_nothing.visual_tokens import REQUIRED_FIGURES


def test_real_pipeline_without_render_or_notebook(pipeline_case):
    report = validate_project(
        pipeline_case.root,
        pipeline_case.output,
        require_render=False,
        specification_dir=pipeline_case.specifications,
    )
    assert report.all_pass
    assert {path.stem for path in (pipeline_case.output / "figures").glob("*.png")} == REQUIRED_FIGURES
    assert {"task_settings", "boundary_task"} <= REQUIRED_FIGURES
    assert (pipeline_case.output / "data/agents.csv").read_text().count("\n") == 9
    with np.load(pipeline_case.output / "data/source_reconstruction.npz", allow_pickle=False) as archive:
        assert archive["baseline"].shape == (1000, 7, 5, 12)
        assert np.isfinite(archive["baseline"]).all()
        assert len(archive.files) == 7


def test_saved_record_reanalysis_matches_fresh_pipeline_without_changing_observations(pipeline_case):
    original = read_bundle(pipeline_case.output)

    replayed = reanalyze(original, pipeline_case.output / "specifications")

    assert replayed == original
    assert replayed.study is original.study
    assert replayed.practice.rows is original.practice.rows
    assert replayed.gaze.transfer is original.gaze.transfer
    assert replayed.gaze.episodes is original.gaze.episodes
    assert replayed.boundary_gaze is original.boundary_gaze


@pytest.mark.parametrize("missing", [None, "analysis.gnn.md", "gratitude.gnn.md"])
def test_incomplete_selection_cannot_reuse_or_overwrite_preserved_models(
    pipeline_case, tmp_path, missing
):
    preserved = pipeline_case.output / "specifications"
    before = {path.name: path.read_bytes() for path in preserved.iterdir() if path.is_file()}
    receipt = pipeline_case.output / "data/source_tree.json"
    original_receipt = receipt.read_bytes()
    selected = tmp_path / "selected"
    if missing is None:
        selected.mkdir()
    else:
        shutil.copytree(preserved, selected)
        changed_model = next(path for path in selected.glob("*.gnn.md") if path.name != missing)
        changed_model.write_text(changed_model.read_text() + "\n")
        (selected / missing).unlink()

    with pytest.raises(FileNotFoundError):
        run_pipeline(
            pipeline_case.root,
            pipeline_case.output,
            render=False,
            notebook=False,
            specification_dir=selected,
        )

    assert {path.name: path.read_bytes() for path in preserved.iterdir() if path.is_file()} == before
    assert receipt.read_bytes() == original_receipt
