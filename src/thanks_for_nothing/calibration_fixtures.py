# Copyright (c) 2026 Daniel Ari Friedman
"""Known-answer statistical stressors independent of gratitude model parameters."""

from enum import StrEnum
from math import sqrt
from typing import Final, assert_never

import numpy as np
from numpy.typing import NDArray

GAUSSIAN_SHIFT: Final = 1.0
HEAVY_TAIL_DF: Final = 3
HETEROGENEOUS_SCALES: Final = (0.25, 0.5, 1.0, 2.0, 4.0)
BERNOULLI_PROBABILITY: Final = 0.1


class Fixture(StrEnum):
    """Controls span symmetry, skew, heterogeneous variance and discrete boundaries."""

    GAUSSIAN = "symmetric_null"
    SHIFT = "one_sd_positive_control"
    HEAVY_TAIL = "symmetric_heavy_tail"
    SKEW = "centered_exponential"
    HETEROGENEOUS = "heterogeneous_gaussian"
    DISCRETE = "centered_bernoulli"


LABELS: Final = {
    Fixture.GAUSSIAN: "Gaussian null",
    Fixture.SHIFT: f"Gaussian shift (+{GAUSSIAN_SHIFT:g} SD)",
    Fixture.HEAVY_TAIL: f"Heavy-tail null (t, df={HEAVY_TAIL_DF})",
    Fixture.SKEW: "Skewed null (exponential)",
    Fixture.HETEROGENEOUS: f"{len(HETEROGENEOUS_SCALES)} Gaussian variance strata",
    Fixture.DISCRETE: f"Discrete null (Bernoulli {BERNOULLI_PROBABILITY:g})",
}
TRUE_MEAN: Final = {
    Fixture.GAUSSIAN: 0.0,
    Fixture.SHIFT: GAUSSIAN_SHIFT,
    Fixture.HEAVY_TAIL: 0.0,
    Fixture.SKEW: 0.0,
    Fixture.HETEROGENEOUS: 0.0,
    Fixture.DISCRETE: 0.0,
}
SYMMETRY: Final = {
    Fixture.GAUSSIAN: "satisfied under the zero-mean null",
    Fixture.SHIFT: "non-null positive control",
    Fixture.HEAVY_TAIL: "satisfied under the zero-mean null",
    Fixture.SKEW: "violated: zero mean does not imply sign symmetry",
    Fixture.HETEROGENEOUS: (f"satisfied separately within {len(HETEROGENEOUS_SCALES)} zero-mean strata"),
    Fixture.DISCRETE: f"violated: centered Bernoulli {BERNOULLI_PROBABILITY:g} is asymmetric",
}


def sample_fixture(fixture: Fixture, rng: np.random.Generator, sample_size: int) -> NDArray[np.float64]:
    """Generate paired differences with a known mean; no synthetic human outcomes."""
    match fixture:
        case Fixture.GAUSSIAN:
            return rng.normal(0, 1, (1, sample_size))
        case Fixture.SHIFT:
            return rng.normal(GAUSSIAN_SHIFT, 1, (1, sample_size))
        case Fixture.HEAVY_TAIL:
            return np.asarray(
                rng.standard_t(HEAVY_TAIL_DF, (1, sample_size)) / sqrt(HEAVY_TAIL_DF), dtype=np.float64
            )
        case Fixture.SKEW:
            return np.asarray(rng.exponential(1, (1, sample_size)) - 1, dtype=np.float64)
        case Fixture.HETEROGENEOUS:
            scales = np.array(HETEROGENEOUS_SCALES, dtype=np.float64)[:, None]
            return np.asarray(
                rng.normal(0, 1, (len(HETEROGENEOUS_SCALES), sample_size)) * scales, dtype=np.float64
            )
        case Fixture.DISCRETE:
            return np.asarray(
                rng.binomial(1, BERNOULLI_PROBABILITY, (1, sample_size)) - BERNOULLI_PROBABILITY,
                dtype=np.float64,
            )
        case _:
            assert_never(fixture)
