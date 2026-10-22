# Copyright (c) 2026 Daniel Ari Friedman
"""Re-admit each changed GNN declaration before a paired sensitivity experiment."""

import json
import shutil
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar

import numpy as np
from pydantic import BaseModel, ConfigDict, JsonValue, TypeAdapter

from thanks_for_nothing.contracts import Condition, ContractError, StudyDesign
from thanks_for_nothing.experiments import run_study


class _Setting(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    parameters: dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class SensitivityCell:
    """One re-admitted declaration and its matched-recall contrast."""

    prior_concentration: float
    recall_precision: float
    replicates_per_stratum: int
    optimism_positive_minus_random: float
    brier_positive_minus_random: float
    model_sha256: str
    pairing_controls_pass: bool


@dataclass(frozen=True, slots=True)
class SensitivityAudit:
    """Conditional model-grid results with explicit pairing controls."""

    schema: str
    rows: tuple[SensitivityCell, ...]
    controls: dict[str, bool]
    evidence_ceiling: str


def build_sensitivity_audit(
    design: StudyDesign, *, specification_dir: Path | None = None
) -> SensitivityAudit:
    """Change GNN parameter JSON, parse it through upstream admission, then execute.

    Shared seeds across grid cells reduce numerical comparison noise. The grid
    is conditional sensitivity, not additional independently sampled evidence.
    """
    source_dir = specification_dir or Path(str(files("thanks_for_nothing").joinpath("models")))
    design_parameters = TypeAdapter(dict[str, JsonValue]).validate_json(
        TypeAdapter(StudyDesign).dump_json(design)
    )
    rows: list[SensitivityCell] = []
    with TemporaryDirectory(prefix="tfn-sensitivity-") as name:
        target = Path(name) / "models"
        _ = shutil.copytree(source_dir, target)
        path = target / "gratitude.gnn.md"
        original = path.read_text()
        settings_line = next(line for line in original.splitlines() if line.startswith("settings="))
        settings = _Setting.model_validate_json(settings_line.removeprefix("settings=")[1:-1])
        for concentration in design.sensitivity_prior_concentrations:
            for precision in design.sensitivity_recall_precisions:
                changed = settings.model_copy(deep=True)
                changed.parameters.update(design_parameters)
                changed.parameters.update(
                    prior_concentration=concentration,
                    recall_precision=precision,
                    replicates=design.sensitivity_replicates,
                )
                declaration = "settings=" + json.dumps([changed.model_dump()], separators=(",", ":"))
                _ = path.write_text(original.replace(settings_line, declaration))
                study = run_study(specification_dir=target)
                positive = [row for row in study.rows if row.condition == Condition.POSITIVE]
                random = [row for row in study.rows if row.condition == Condition.RANDOM]
                if len(positive) != len(random):
                    message = "Sensitivity contrast must preserve paired conditions"
                    raise ContractError(message)
                optimism = [
                    (p.optimism_post - p.optimism_pre) - (r.optimism_post - r.optimism_pre)
                    for p, r in zip(positive, random, strict=True)
                ]
                brier = [
                    (p.brier_post - p.brier_pre) - (r.brier_post - r.brier_pre)
                    for p, r in zip(positive, random, strict=True)
                ]
                rows.append(
                    SensitivityCell(
                        concentration,
                        precision,
                        study.design.replicates,
                        float(np.mean(optimism)),
                        float(np.mean(brier)),
                        study.model_sha256,
                        all(study.controls.values()),
                    )
                )
    return SensitivityAudit(
        "thanks_for_nothing.sensitivity.v1",
        tuple(rows),
        {
            "each_grid_cell_re_admitted": len({r.model_sha256 for r in rows}) == len(rows),
            "paired_exposures_preserved": all(r.pairing_controls_pass for r in rows),
        },
        "Conditional paired sensitivity on a fixed model grid; no human population inference.",
    )
