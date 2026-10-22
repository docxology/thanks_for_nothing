# Copyright (c) 2026 Daniel Ari Friedman
"""Consume real pinned GNN parsing and Realizing Emptiness admission."""

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import ClassVar, Final

import numpy as np
from modeling.registry import parse_model
from pydantic import BaseModel, ConfigDict

from thanks_for_nothing.contracts import ContractError, Design

PROBABILITY_TOLERANCE: Final = 1e-8


class Tensors(BaseModel):
    """Immutable canonical arrays at the external admission boundary."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    A: tuple[tuple[float, ...], ...]
    B: tuple[tuple[tuple[float, ...], ...], ...]
    C: tuple[float, ...]
    D: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class AdmittedModel:
    """Parsed tensor contract bound to exact source bytes."""

    model_id: str
    source_hash: str
    tensors: Tensors
    parameters_json: str
    source_text: str


def load_model(model_id: str, specification_dir: Path | None = None) -> AdmittedModel:
    """Reject missing/invalid files using both upstream and local contracts."""
    root = specification_dir or Path(str(files("thanks_for_nothing").joinpath("models")))
    source = (root / f"{model_id}.gnn.md").read_text(encoding="utf-8")
    return admit_model_source(source, model_id)


@lru_cache(maxsize=128)
def admit_model_source(source: str, model_id: str) -> AdmittedModel:
    """Admit standalone GNN bytes through the real upstream parser and canonical POMDP builder."""
    model = parse_model(source, model_id)
    tensors = Tensors.model_validate(model.tensors)
    for matrix in (np.asarray(tensors.A), np.asarray(tensors.B)):
        if (
            not np.isfinite(matrix).all()
            or (matrix < 0).any()
            or np.max(np.abs(np.sum(matrix, axis=0, dtype=np.float64) - 1)) >= PROBABILITY_TOLERANCE
        ):
            message = "A and B must be normalized probability columns"
            raise ContractError(message)
    if (
        not np.isfinite(tensors.C).all()
        or min(tensors.D) < 0
        or abs(sum(tensors.D) - 1) >= PROBABILITY_TOLERANCE
    ):
        message = "C must be finite and D a probability distribution"
        raise ContractError(message)
    return AdmittedModel(model_id, model.source_hash, tensors, json.dumps(model.parameters), source)


def load_study(specification_dir: Path | None = None) -> tuple[AdmittedModel, Design]:
    """Admit the binary world and normalized, mode-specific news readout."""
    model = load_model("gratitude", specification_dir)
    design = Design.model_validate_json(model.parameters_json)
    if np.asarray(model.tensors.A).shape != (3, 2) or np.asarray(model.tensors.B).shape != (2, 2, 1):
        message = "Gratitude requires three observations and two hidden states"
        raise ContractError(message)
    if not design.luckiness or len(set(design.luckiness)) != len(design.luckiness):
        message = "Luckiness strata must be nonempty and unique"
        raise ContractError(message)
    if not 0 < design.task_prior_min < design.task_prior_max < 1:
        message = "Task prior bounds must lie strictly within (0,1)"
        raise ContractError(message)
    for matrix in (design.optimism_well, design.optimism_poor):
        if np.max(np.abs(np.sum(matrix, axis=0, dtype=np.float64) - 1)) >= PROBABILITY_TOLERANCE:
            message = "News likelihood columns must normalize"
            raise ContractError(message)
    return model, design
