# Copyright (c) 2026 Daniel Ari Friedman
"""Declared visual tasks and paired agent-level gaze records."""

from dataclasses import dataclass
from typing import ClassVar, Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.intervals import MeanIntervals
from thanks_for_nothing.joint_contracts import JointDesign

EVIDENCE_ORACLE_TOLERANCE: Final = 1e-10
TransferBridge = Literal["likelihood", "posterior_readout"]

GazeCondition = Literal[
    "pragmatic_restricted",
    "pragmatic_open",
    "inquiry_open",
    "inquiry_restricted",
    "sham",
    "uniform_open",
]


class GazeContext(BaseModel):
    """An exogenous sequence of candidate channels, shared across policies."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(min_length=1)
    candidates: tuple[int, ...] = Field(min_length=1)


class GazeDesign(BaseModel):
    """All new sampling, registration and policy choices come from one GNN declaration."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    seed: int = Field(ge=0)
    source_seed: Literal[42]
    source_steps: Literal[1000]
    source_runs: Literal[5]
    transfer_steps: int = Field(ge=2)
    transfer_ambiguity_weight: float = Field(ge=0, allow_inf_nan=False)
    transfer_precision: float = Field(gt=0, allow_inf_nan=False)
    transfer_state_map: tuple[tuple[float, ...], ...]
    transfer_comparisons: tuple[tuple[str, str], ...]
    trajectory_steps: int = Field(ge=2)
    example_strata: tuple[float, ...] = Field(min_length=1)
    example_window: int = Field(ge=0)
    replicates: int = Field(ge=2)
    steps: int = Field(ge=2)
    bootstrap_draws: int = Field(ge=1)
    joint: JointDesign
    action_precision: float = Field(gt=0, allow_inf_nan=False)
    information_weight: float = Field(ge=0, allow_inf_nan=False)
    saccade_cost: float = Field(ge=0, allow_inf_nan=False)
    structural_model: Literal["emptiness_practice"]
    initial_location: int = Field(ge=0)
    coordinates: tuple[tuple[float, float], ...] = Field(min_length=1)
    regions: tuple[int, ...] = Field(min_length=1)
    channels: tuple[tuple[tuple[float, ...], ...], ...]
    contexts: tuple[GazeContext, ...] = Field(min_length=1)
    conditions: tuple[GazeCondition, ...] = Field(min_length=2)
    comparisons: tuple[tuple[GazeCondition, GazeCondition], ...]


@dataclass(frozen=True, slots=True)
class SourceGaze:
    """Original five-pair numeric run; the source contains no after-intervention run."""

    source_sha256: str
    positive_states: tuple[tuple[int, ...], ...]
    negative_states: tuple[tuple[int, ...], ...]
    positive_percent: tuple[float, ...]
    negative_percent: tuple[float, ...]
    published_before_matches: bool
    after_intervention_available: Literal[False]


@dataclass(frozen=True, slots=True)
class TransferGaze:
    """One paired learning agent, not an independent set of fixation samples."""

    bridge: TransferBridge
    condition: str
    luckiness: float
    replicate: int
    paired_id: str
    exposure_sha256: str
    prior_well: float
    posterior_well: float
    pre_policy: tuple[float, ...]
    post_policy: tuple[float, ...]
    pre_locations: tuple[int, ...]
    post_locations: tuple[int, ...]
    positive_policy_change: float
    balanced_loss_change: float


@dataclass(frozen=True, slots=True)
class GazeEpisode:
    """A sampled active-sensing episode, with population risk scored across the whole scene."""

    context: str
    replicate: int
    window: int
    condition: GazeCondition
    true_candidate: int
    exposure_sha256: str
    locations: tuple[int, ...]
    observations: tuple[int, ...]
    final_posterior: tuple[float, ...]
    mean_balanced_log_loss: float
    positive_occupancy: float
    mean_information_gain: float
    mean_movement_cost: float
    native_evidence_max_error: float


@dataclass(frozen=True, slots=True)
class GazeContrast:
    """Exploratory pointwise intervals over complete paired simulation replicates."""

    experiment: Literal["transfer", "active"]
    context: str
    condition: str
    reference: str
    endpoint: str
    intervals: MeanIntervals
    units: int


@dataclass(frozen=True, slots=True)
class GazeAudit:
    """Separate exact source reconstruction, learned transfer and authored active sensing."""

    schema: str
    design: GazeDesign
    model_sha256: str
    structural_model_sha256: str
    transfer_model_sha256: tuple[str, ...]
    learning_parameters_sha256: str
    source: SourceGaze
    transfer: tuple[TransferGaze, ...]
    episodes: tuple[GazeEpisode, ...]
    contrasts: tuple[GazeContrast, ...]
    controls: dict[str, bool]
    all_controls_pass: bool
