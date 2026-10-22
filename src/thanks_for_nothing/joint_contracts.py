# Copyright (c) 2026 Daniel Ari Friedman
"""Joint uncertainty targets, explicit failure states and GNN-declared budgets."""

from dataclasses import dataclass
from typing import ClassVar, Final, Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

MIN_PAIRED_UNITS: Final = 2
BLOCK_DIMENSIONS: Final = 3


class JointDesign(BaseModel):
    """Numerical budgets for a separately declared exploratory joint confidence region."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    seed: int = Field(ge=0)
    draws: int = Field(ge=2)
    confidence: float = Field(gt=0, lt=1, allow_inf_nan=False)
    monte_carlo_confidence: float = Field(gt=0, lt=1, allow_inf_nan=False)
    calibration_experiments: int = Field(ge=2)
    calibration_units: int = Field(ge=2)
    calibration_draws: int = Field(ge=2)


@dataclass(frozen=True, slots=True)
class JointBlock:
    """One independent block: fixed strata by paired units by contrast columns."""

    name: str
    keys: tuple[str, ...]
    values: NDArray[np.float64]
    exact_zero: tuple[bool, ...]


@dataclass(frozen=True, slots=True)
class JointInterval:
    """A family member; an observed constant is not automatically an exact identity."""

    key: str
    mean: float
    standard_error: float
    low: float | None
    high: float | None
    status: Literal["estimated", "mechanism_exact", "unavailable_constant"]


@dataclass(frozen=True, slots=True)
class JointRegion:
    """A centered empirical-bootstrap max-root rectangle, not bootstrap t or stepdown."""

    confidence: float
    draws: int
    critical_value: float | None
    critical_mc_low: float | None
    critical_mc_high: float | None
    monte_carlo_confidence: float
    blocks: tuple[tuple[str, int, int], ...]
    intervals: tuple[JointInterval, ...]
    status: Literal["complete", "partial", "unavailable", "mechanism_exact"]
