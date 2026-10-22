# Copyright (c) 2026 Daniel Ari Friedman
import json
from dataclasses import replace
from statistics import mean

import pytest

from tests.support.models import small_model_directory
from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.experiments import run_study
from thanks_for_nothing.sensitivity import build_sensitivity_audit


def test_sensitivity_replays_admitted_design_and_unique_grid(tmp_path):
    models = small_model_directory(tmp_path)
    design = replace(run_study(specification_dir=models).design, seed=10213)

    audit = build_sensitivity_audit(design, specification_dir=models)

    assert audit == build_sensitivity_audit(design, specification_dir=models)
    assert all(audit.controls.values())
    assert len(audit.rows) == len({row.model_sha256 for row in audit.rows}) == 9
    assert {row.replicates_per_stratum for row in audit.rows} == {2}


def test_sensitivity_matches_direct_gnn_execution_with_supplied_seed(tmp_path):
    models = small_model_directory(tmp_path)
    design = replace(run_study(specification_dir=models).design, seed=10213)
    audit = build_sensitivity_audit(design, specification_dir=models)
    cell = audit.rows[0]
    path = models / "gratitude.gnn.md"
    original = path.read_text()
    line = next(line for line in original.splitlines() if line.startswith("settings="))
    settings = json.loads(line.removeprefix("settings="))
    settings[0]["parameters"].update(
        seed=design.seed,
        replicates=design.sensitivity_replicates,
        prior_concentration=cell.prior_concentration,
        recall_precision=cell.recall_precision,
    )
    path.write_text(original.replace(line, "settings=" + json.dumps(settings)))

    direct = run_study(specification_dir=models)

    positive = [r for r in direct.rows if r.condition == Condition.POSITIVE]
    random = [r for r in direct.rows if r.condition == Condition.RANDOM]
    optimism = mean(
        (p.optimism_post - p.optimism_pre) - (r.optimism_post - r.optimism_pre)
        for p, r in zip(positive, random, strict=True)
    )
    brier = mean(
        (p.brier_post - p.brier_pre) - (r.brier_post - r.brier_pre)
        for p, r in zip(positive, random, strict=True)
    )
    assert cell.optimism_positive_minus_random == pytest.approx(optimism)
    assert cell.brier_positive_minus_random == pytest.approx(brier)
    assert direct.design.seed == design.seed


def test_sensitivity_rejects_invalid_gnn_instead_of_falling_back(tmp_path):
    models = small_model_directory(tmp_path)
    design = run_study(specification_dir=models).design
    path = models / "gratitude.gnn.md"
    path.write_text(path.read_text().replace("A=[[0.7,0.2]", "A=[[7.0,0.2]"))

    with pytest.raises(ValueError, match=r"normaliz|probabilit"):
        build_sensitivity_audit(design, specification_dir=models)
