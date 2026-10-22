# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

@dataclass(frozen=True)
class BoundaryScreen:
    channel_count: int
    bit_names: tuple[str, ...]
    def validate(self) -> None: ...

@dataclass(frozen=True)
class QRFDeployment:
    name: str
    sector_labels: tuple[str, ...]
    metacognitive_access: float
    prior_precision: float
    def validate(self, screen: BoundaryScreen) -> None: ...
    @property
    def is_dual(self) -> bool: ...

@dataclass(frozen=True)
class SeparationPrior:
    precision: float
    enforced: bool = True
    def admissible(self, deployments: tuple[QRFDeployment, ...]) -> tuple[QRFDeployment, ...]: ...

@dataclass(frozen=True)
class FreeEnergyTerms:
    accuracy: float
    complexity: float
    noise: float = 0.0
    @classmethod
    def from_distributions(
        cls,
        posterior: NDArray[np.float64],
        prior: NDArray[np.float64],
        log_likelihood: NDArray[np.float64],
        *,
        noise: float = 0.0,
        base: float = 2.0,
    ) -> FreeEnergyTerms: ...
    @property
    def free_energy(self) -> float: ...

@dataclass(frozen=True)
class BMRComparison:
    full_model: FreeEnergyTerms
    reduced_model: FreeEnergyTerms
    @property
    def delta_complexity(self) -> float: ...
    @property
    def delta_accuracy(self) -> float: ...
    @property
    def delta_free_energy(self) -> float: ...
    @property
    def prunes_prior(self) -> bool: ...

def complexity_kl(
    posterior: NDArray[np.float64], prior: NDArray[np.float64], *, base: float = 2.0
) -> float: ...
