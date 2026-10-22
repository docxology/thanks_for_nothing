# Copyright (c) 2026 Daniel Ari Friedman
"""Declared scene/encoding inquiry and complete paired simulation records."""

from dataclasses import dataclass
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.joint_contracts import JointRegion

BoundaryCondition = Literal["visual", "integrated", "boundary_only", "uniform", "restricted", "sham"]
BoundaryRegime = Literal["diagnostic", "label_only"]
BoundaryEndpoint = Literal["anchored_regret", "boundary_brier"]


class BoundaryDesign(BaseModel):
    """All new experimental choices are admitted from the packaged GNN declaration."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    seed: int = Field(ge=0)
    replicates: int = Field(ge=2)
    steps: int = Field(ge=2)
    prefixes: tuple[int, ...] = Field(min_length=1)
    scene_maps: tuple[tuple[int, ...], ...]
    probe_reliabilities: tuple[float, ...] = Field(min_length=1)
    probe_costs: tuple[float, ...] = Field(min_length=1)
    regimes: tuple[BoundaryRegime, ...]
    conditions: tuple[BoundaryCondition, ...]
    comparisons: tuple[tuple[BoundaryCondition, BoundaryCondition], ...]
    endpoints: tuple[BoundaryEndpoint, ...]
    gaze_model: Literal["gaze"]
    anchor_mapping: Literal[0]
    joint_seed: int = Field(ge=0)


@dataclass(frozen=True, slots=True)
class BoundaryEpisode:
    """One independent potential-outcome unit observed by one of six paired policies."""

    regime: BoundaryRegime
    scene: int
    boundary: int
    replicate: int
    condition: BoundaryCondition
    exposure_sha256: str
    queries: tuple[int, ...]
    outcomes: tuple[int, ...]
    final_joint: tuple[float, ...]
    final_scene: tuple[float, ...]
    final_boundary: tuple[float, ...]
    boundary_entropy: float
    boundary_brier: float
    anchored_regret: float
    mean_scene_regret: float
    mean_cost: float
    boundary_query_fraction: float
    native_evidence_max_error: float


@dataclass(frozen=True, slots=True)
class BoundaryConvergence:
    """Nested independent replicate prefixes, with fixed scene strata and no adaptive stopping."""

    regime: BoundaryRegime
    boundary: int
    condition: BoundaryCondition
    reference: BoundaryCondition
    endpoint: BoundaryEndpoint
    replicates_per_stratum: int
    mean: float
    standard_error: float


@dataclass(frozen=True, slots=True)
class BoundaryGazeAudit:
    """A separate exploratory family; reference intervention and null retain their assumptions."""

    schema: str
    design: BoundaryDesign
    model_sha256: str
    gaze_model_sha256: str
    structural_model_sha256: str
    episodes: tuple[BoundaryEpisode, ...]
    region: JointRegion
    exact_offsets: tuple[tuple[str, float], ...]
    convergence: tuple[BoundaryConvergence, ...]
    controls: dict[str, bool]
    all_controls_pass: bool
