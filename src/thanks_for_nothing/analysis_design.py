# Copyright (c) 2026 Daniel Ari Friedman
"""Admit the shared inference protocol separately from mathematical control targets."""

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.joint_contracts import MIN_PAIRED_UNITS
from thanks_for_nothing.specifications import load_model


class AnalysisDesign(BaseModel):
    """Declared statistical levels, stream namespaces and diagnostic budgets."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    alpha: float = Field(gt=0, lt=1, allow_inf_nan=False)
    statistics_seed_offset: int = Field(ge=0)
    heterogeneity_seed_offset: int = Field(ge=0)
    calibration_seed_offset: int = Field(ge=0)
    diagnostic_prefixes: tuple[int, ...] = Field(min_length=2)
    notebook_replicates: int = Field(ge=2)
    notebook_draws: int = Field(ge=2)
    notebook_timeout_seconds: int = Field(ge=1)
    reconstruction_seed: int = Field(ge=0, le=2**32 - 1)
    reconstruction_agents: int = Field(ge=1)
    reconstruction_days: int = Field(ge=1)
    reconstruction_steps: int = Field(ge=1)
    reconstruction_audit_agents: int = Field(ge=1)

    @field_validator("diagnostic_prefixes")
    @classmethod
    def _ordered_prefixes(cls, values: tuple[int, ...]) -> tuple[int, ...]:
        if min(values) < MIN_PAIRED_UNITS or tuple(sorted(set(values))) != values:
            message = "Diagnostic prefixes must be distinct increasing counts of at least two units"
            raise ContractError(message)
        return values


def load_analysis(specification_dir: Path | None = None) -> AnalysisDesign:
    """Use the pinned GNN parser for the actual packaged or supplied protocol."""
    return AnalysisDesign.model_validate_json(load_model("analysis", specification_dir).parameters_json)
