# Copyright (c) 2026 Daniel Ari Friedman
"""Typed boundaries for preference, access, model comparison and held-out assessment."""

from dataclasses import dataclass
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.intervals import MeanIntervals

Condition = Literal["rigid", "inquiry", "no_preference", "sham", "no_access"]


class Deployment(BaseModel):
    """A declared assignment of operational labels to a common boundary screen."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(min_length=1)
    labels: tuple[str, ...] = Field(min_length=1)


class Context(BaseModel):
    """Exogenous probability schedule, shared across compared policies."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(min_length=1)
    probabilities: tuple[float, ...] = Field(min_length=2)


class PracticeDesign(BaseModel):
    """Every scientific policy and sampling choice is admitted from GNN settings."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    seed: int = Field(ge=0)
    replicates: int = Field(ge=2)
    calibration_samples: int = Field(ge=1)
    assessment_samples: int = Field(ge=1)
    bootstrap_draws: int = Field(ge=1)
    action_precision: float = Field(ge=0, allow_inf_nan=False)
    practice_cost: float = Field(ge=0, allow_inf_nan=False)
    examinability_preference: float = Field(ge=0, allow_inf_nan=False)
    previous_gain_weight: float = Field(ge=0, allow_inf_nan=False)
    metacognitive_access: float = Field(ge=0, le=1, allow_inf_nan=False)
    prior_precision: float = Field(ge=0, allow_inf_nan=False)
    deployments: tuple[Deployment, ...] = Field(min_length=2)
    contexts: tuple[Context, ...] = Field(min_length=1)
    conditions: tuple[Condition, ...] = Field(min_length=2)


@dataclass(frozen=True, slots=True)
class PriorComparison:
    """Exact finite VFE in nats; both posteriors are recomputed on calibration data."""

    restricted_free_energy: float
    open_free_energy: float
    delta_complexity: float
    delta_accuracy: float
    delta_free_energy: float
    restricted_forecast: float
    open_forecast: float
    oracle_error: float
    log_bayes_factor: float
    prefers_open: bool


@dataclass(frozen=True, slots=True)
class PracticeRow:
    """One window; counterfactual diagnostics are distinct from information used by policy."""

    context: str
    replicate: int
    window: int
    condition: Condition
    process_probability: float
    calibration_zero_count: int
    assessment_zero_count: int
    exposure_sha256: str
    action_probability: float
    practiced: bool
    effective_access: bool
    previous_observed_gain: float
    uses_open_family: bool
    forecast: float
    heldout_log_loss: float
    incurred_cost: float
    comparison: PriorComparison


@dataclass(frozen=True, slots=True)
class PracticeContrast:
    """Pointwise exploratory interval over paired replicate means, not window pseudoreplicates."""

    context: str
    condition: Condition
    heldout_loss_difference: MeanIntervals
    mean_practice_rate: float
    mean_access_rate: float
    mean_cost: float


@dataclass(frozen=True, slots=True)
class PracticeAudit:
    """Separate extension experiment with exact controls and explicit upstream binding."""

    schema: str
    design: PracticeDesign
    model_sha256: str
    rows: tuple[PracticeRow, ...]
    contrasts: tuple[PracticeContrast, ...]
    controls: dict[str, bool]
    all_controls_pass: bool


@dataclass(frozen=True, slots=True)
class ExactDecisionRow:
    """One exhaustive calibration count with rational evidence and imported numerical checks."""

    zero_count: int
    log_bayes_factor: float
    native_log_bayes_factor: float
    supports_open: bool
    native_supports_open: bool
    restricted_forecast: float
    evidence_selected_forecast: float
    numerical_max_error: float


@dataclass(frozen=True, slots=True)
class ExactOperatingPoint:
    """Finite count probabilities and expected log loss conditional on an effective inquiry."""

    process_probability: float
    count_probabilities: tuple[float, ...]
    open_probability_numerator: str
    open_probability_denominator: str
    open_probability: float
    log10_open_probability: float | None
    restricted_expected_log_loss: float
    selected_expected_log_loss: float
    expected_loss_difference: float
    probability_total_exact: bool


@dataclass(frozen=True, slots=True)
class ExactDecisionAudit:
    """Exhaustive one-window selection, distinct from the repeated stochastic practice policy."""

    schema: str
    model_sha256: str
    calibration_samples: int
    restricted_prior_mass: float
    rows: tuple[ExactDecisionRow, ...]
    operating_points: tuple[ExactOperatingPoint, ...]
    controls: dict[str, bool]
    all_controls_pass: bool
