# Copyright (c) 2026 Daniel Ari Friedman
"""Immutable, JSON-compatible study records and strict admission parameters."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict

Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Probability = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Count = Annotated[int, Field(gt=0, strict=True)]


class ContractError(ValueError):
    """An explicit numerical or declaration contract was violated."""

    detail: str

    def __init__(self, detail: str) -> None:
        """Retain an explicit failure detail for the caller."""
        self.detail = detail
        super().__init__(detail)


class Condition(StrEnum):
    """Paired interventions; absence valuation does not alter inference."""

    NO_RECALL = "no_recall"
    POSITIVE = "positive_recall"
    RANDOM = "matched_random_recall"
    ABSENCE = "absence_appreciation"


class Design(BaseModel):
    """Study knobs admitted once from the GNN declaration."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    seed: Annotated[int, Field(ge=0, strict=True)]
    replicates: Count
    luckiness: tuple[Probability, ...]
    baseline_days: Count
    intervention_days: Count
    steps_per_day: Count
    recall_count: Count
    recall_precision: Positive
    learning_rate: Positive
    forgetting: Annotated[float, Field(gt=0, le=1)]
    prior_concentration: Positive
    bootstrap_draws: Count
    permutation_draws: Count
    assessment_trials: Count
    task_prior_min: Probability
    task_prior_max: Probability
    sensitivity_replicates: Count
    sensitivity_prior_concentrations: tuple[Positive, ...]
    sensitivity_recall_precisions: tuple[Positive, ...]
    calibration_replicates: Count
    calibration_sample_size: Count
    calibration_bootstrap_draws: Count
    calibration_permutation_draws: Count
    evaluation_trials: Count
    reference_hazard: Probability
    harm_cost: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    optimism_well: tuple[tuple[Probability, Probability], tuple[Probability, Probability]]
    optimism_poor: tuple[tuple[Probability, Probability], tuple[Probability, Probability]]


@dataclass(frozen=True, slots=True)
class StudyDesign:
    """Serializable copy of the admitted design, including explicit matrices."""

    seed: int
    replicates: int
    luckiness: tuple[float, ...]
    baseline_days: int
    intervention_days: int
    steps_per_day: int
    recall_count: int
    recall_precision: float
    learning_rate: float
    forgetting: float
    prior_concentration: float
    bootstrap_draws: int
    permutation_draws: int
    assessment_trials: int
    task_prior_min: float
    task_prior_max: float
    sensitivity_replicates: int
    sensitivity_prior_concentrations: tuple[float, ...]
    sensitivity_recall_precisions: tuple[float, ...]
    calibration_replicates: int
    calibration_sample_size: int
    calibration_bootstrap_draws: int
    calibration_permutation_draws: int
    evaluation_trials: int
    reference_hazard: float
    harm_cost: float
    optimism_well: tuple[tuple[float, float], tuple[float, float]]
    optimism_poor: tuple[tuple[float, float], tuple[float, float]]


@dataclass(frozen=True, slots=True)
class AgentResult:
    """One independent replicate in one paired condition."""

    condition: Condition
    luckiness: float
    replicate: int
    paired_id: str
    pre_world_well: float
    post_world_well: float
    brier_pre: float
    brier_post: float
    nll_pre: float
    nll_post: float
    entropy_post: float
    optimism_pre: float
    optimism_post: float
    appreciation: float
    mean_recall_count: float
    exposure_sha256: str


@dataclass(frozen=True, slots=True)
class DailyTrace:
    """Daily mean online posterior retained for every independent paired unit."""

    condition: Condition
    luckiness: float
    replicate: int
    day: int
    world_well: float


class StudyControls(TypedDict):
    """Derived pairing invariants, not assertions of intervention efficacy."""

    identical_exposures: bool
    identical_baselines: bool
    absence_belief_null: bool
    dose_matched: bool


@dataclass(frozen=True, slots=True)
class StudyResult:
    """A pure experiment result; dataclasses.asdict is JSON serializable."""

    design: StudyDesign
    rows: tuple[AgentResult, ...]
    traces: tuple[DailyTrace, ...]
    controls: StudyControls
    model_sha256: str


@dataclass(frozen=True, slots=True)
class LearnedChannel:
    """Frozen training parameters; neither matrix consumes assessment observations."""

    condition: Condition
    luckiness: float
    replicate: int
    paired_id: str
    exposure_sha256: str
    pre: tuple[tuple[float, ...], ...]
    post: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, slots=True)
class LearningExperiment:
    """The existing study and its separately retained pre/post learned channels."""

    study: StudyResult
    parameters: tuple[LearnedChannel, ...]


@dataclass(frozen=True, slots=True)
class ReceiptRecord:
    """Stable numerical subset of an on-disk native execution receipt."""

    success: bool
    observations: tuple[int, ...]
    actions: tuple[int, ...]
    beliefs: tuple[tuple[float, ...], ...]
    policy_posterior: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, slots=True)
class AttentionCondition:
    """Policy masses from the independent fixed-process counterpart."""

    condition: str
    positive_mass: float
    negative_mass: float
    neutral_mass: float
    actions: tuple[int, ...]
    observations: tuple[int, ...]
    beliefs: tuple[tuple[float, ...], ...]
    policy_posterior: tuple[tuple[float, ...], ...]
    model_sha256: str


class AttentionControls(TypedDict):
    """Numerically discriminating native and process controls."""

    native_receipts_valid: bool
    fixed_process_valid: bool
    c_changes_policy: bool
    d_changes_initial_belief: bool
    exogenous_precision_changes_policy: bool


@dataclass(frozen=True, slots=True)
class AttentionAudit:
    """Matched-model native receipts and separate fixed-process comparison."""

    rows: tuple[AttentionCondition, ...]
    native_receipts: tuple[ReceiptRecord, ...]
    controls: AttentionControls
    all_controls_pass: bool
    claim_boundary: str
