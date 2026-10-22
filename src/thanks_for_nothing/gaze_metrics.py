# Copyright (c) 2026 Daniel Ari Friedman
"""Geometric descriptors of unsmoothed sampled locations, without dwell-time claims."""

from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING, Final

import numpy as np

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_contracts import GazeDesign

if TYPE_CHECKING:
    from thanks_for_nothing.inference import FloatArray

MIN_PATH_SAMPLES: Final = 2


@dataclass(frozen=True, slots=True)
class PathMetrics:
    """Finite sequence coverage, repeats, distance and joint transition entropy."""

    samples: int
    unique_locations: int
    revisit_fraction: float
    mean_step_length: float
    transition_entropy_bits: float
    region_occupancy: tuple[float, ...]
    occupancy_over_uniform_locations: tuple[float, ...]


def path_metrics(locations: tuple[int, ...], design: GazeDesign) -> PathMetrics:
    """Use supplied samples and declared unit-square geometry without interpolation."""
    if len(locations) < MIN_PATH_SAMPLES or any(
        index < 0 or index >= len(design.regions) for index in locations
    ):
        message = "Path metrics require at least two admitted locations"
        raise ContractError(message)
    coordinates = np.asarray(design.coordinates, dtype=np.float64)[list(locations)]
    differences = coordinates[1:] - coordinates[:-1]
    steps: FloatArray = np.sqrt(np.sum(differences**2, axis=1, dtype=np.float64))
    transitions = tuple(pairwise(locations))
    masses = np.asarray(
        [transitions.count(pair) / len(transitions) for pair in set(transitions)], dtype=np.float64
    )
    regions = tuple(design.regions[index] for index in locations)
    occupancy = tuple(regions.count(region) / len(locations) for region in sorted(set(design.regions)))
    return PathMetrics(
        len(locations),
        len(set(locations)),
        1 - len(set(locations)) / len(locations),
        float(np.mean(steps)),
        float(-np.sum(masses * np.log2(masses))),
        occupancy,
        tuple(
            mass / (design.regions.count(region) / len(design.regions))
            for region, mass in enumerate(occupancy)
        ),
    )
