# Copyright (c) 2026 Daniel Ari Friedman
import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_art import copy_artwork
from thanks_for_nothing.gaze_design import load_gaze_task
from thanks_for_nothing.gaze_findings import gaze_interval_findings, gaze_source_findings
from thanks_for_nothing.gaze_metrics import path_metrics
from thanks_for_nothing.gaze_transfer import build_transfer
from thanks_for_nothing.provenance import file_digest

ROOT = Path(__file__).resolve().parents[1]


def test_metrics_known_geometry_and_uniform_location_baseline():
    design = load_gaze_task().design
    result = path_metrics((0, 1, 0), design)
    assert result.unique_locations == 2
    assert result.revisit_fraction == pytest.approx(1 / 3)
    assert result.mean_step_length == pytest.approx(1 / 7)
    assert result.transition_entropy_bits == 1
    assert result.region_occupancy == (1, 0, 0)
    assert result.occupancy_over_uniform_locations == pytest.approx((13 / 5, 0, 0))
    stationary = path_metrics((10, 10, 10), design)
    assert stationary.mean_step_length == stationary.transition_entropy_bits == 0
    assert stationary.occupancy_over_uniform_locations == pytest.approx((0, 0, 13 / 3))


@pytest.mark.parametrize("locations", [(), (0,), (0, -1), (0, 13)])
def test_metrics_invalid_samples_rejected(locations):
    with pytest.raises(ContractError, match="admitted locations"):
        path_metrics(locations, load_gaze_task().design)


@pytest.mark.parametrize(
    "changes",
    [
        {"exposure_sha256": "wrong"},
        {"luckiness": 0.123},
        {"replicate": 99},
        {"pre": ((0.5, 0.5),) * 3},
        {"post": ((1.0, 1.0), (0.0, 0.0), (0.0, 0.0))},
        {"pre": ((float("nan"), 0.1),) * 3},
        {"post": ((0.5, 0.5),) * 2},
    ],
)
def test_invalid_retained_training_channels_rejected(small_gaze, changes):
    directory, experiment, _ = small_gaze
    records = (replace(experiment.parameters[0], **changes), *experiment.parameters[1:])
    with pytest.raises(ContractError, match="training channels"):
        build_transfer(replace(experiment, parameters=records), load_gaze_task(directory), directory)


@pytest.mark.parametrize("kind", ["missing", "duplicate"])
def test_complete_unique_training_identity_required(small_gaze, kind):
    directory, experiment, _ = small_gaze
    records = experiment.parameters[:-1]
    if kind == "duplicate":
        records = (*records, records[0])
    with pytest.raises(ContractError, match="complete, unique"):
        build_transfer(replace(experiment, parameters=records), load_gaze_task(directory), directory)


def test_gaze_tables_include_every_contrast_and_null(small_gaze):
    _, _, audit = small_gaze
    table = gaze_interval_findings(audit)
    estimates = [
        float(line.split("|")[2])
        for line in table.splitlines()
        if line.startswith("| ") and not line.startswith(("| Contrast", "| ---"))
    ]
    assert estimates == pytest.approx([row.intervals.mean for row in audit.contrasts], abs=0.0000005)
    assert len(estimates) == 58
    assert "Unavailable" in table
    assert "82.14" in gaze_source_findings(audit)


def test_artwork_original_bytes_preserved_and_mutation_rejected(tmp_path):
    copy_artwork(None, tmp_path / "output")
    assert file_digest(tmp_path / "output/assets/scream-original.jpg") == file_digest(
        ROOT / "data/artwork/scream-original.jpg"
    )
    root = tmp_path / "source"
    shutil.copytree(ROOT / "data/artwork", root / "data/artwork")
    path = root / "data/artwork/provenance.json"
    receipt = json.loads(path.read_text())
    receipt["sha256"] = "0" * 64
    path.write_text(json.dumps(receipt))
    with pytest.raises(ContractError, match="acquisition receipt"):
        copy_artwork(root, tmp_path / "rejected")
