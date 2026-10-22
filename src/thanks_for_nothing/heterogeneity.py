# Copyright (c) 2026 Daniel Ari Friedman
"""Exploratory world-specific estimation and conditional weighting sensitivity."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

import numpy as np

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.contracts import AgentResult, Condition
from thanks_for_nothing.intervals import MeanIntervals, mean_intervals, quantile_pair
from thanks_for_nothing.outcomes import Endpoint, endpoint_change

ENDPOINTS: Final[tuple[Endpoint, ...]] = ("brier_change", "nll_change", "optimism_change")


@dataclass(frozen=True, slots=True)
class StratumContrast:
    """Pointwise mean uncertainty and paired-unit spread; no subgroup test decision."""

    endpoint: Endpoint
    first: Condition
    second: Condition
    world: float
    units: int
    intervals: MeanIntervals
    q25: float
    median: float
    q75: float
    positive_fraction: float


@dataclass(frozen=True, slots=True)
class WeightingSensitivity:
    """Sensitivity of a mean to weights, conditional on fixed stratum estimates."""

    endpoint: Endpoint
    first: Condition
    second: Condition
    equal_grid: MeanIntervals
    convex_min: float
    convex_max: float
    leave_one_out_min: float | None
    leave_one_out_max: float | None


@dataclass(frozen=True, slots=True)
class HeterogeneityReport:
    """Exploratory diagnostics separate from the eight primary Holm tests."""

    strata: tuple[StratumContrast, ...]
    weighting: tuple[WeightingSensitivity, ...]
    interval_scope: str
    weighting_scope: str


def build_heterogeneity(
    admitted_rows: Sequence[AgentResult],
    seed: int,
    bootstrap_draws: int,
    *,
    analysis: AnalysisDesign | None = None,
) -> HeterogeneityReport:
    """Describe a complete paired design already admitted by the statistics boundary."""
    protocol = load_analysis() if analysis is None else analysis
    lookup = {(r.luckiness, r.replicate, r.condition): r for r in admitted_rows}
    worlds = sorted({r.luckiness for r in admitted_rows})
    replicates = sorted({r.replicate for r in admitted_rows})
    strata: list[StratumContrast] = []
    weighting: list[WeightingSensitivity] = []
    for endpoint in ENDPOINTS:
        for second in (Condition.NO_RECALL, Condition.RANDOM):
            first = Condition.POSITIVE
            differences = np.asarray(
                [
                    [
                        endpoint_change(lookup[world, rep, first], endpoint)
                        - endpoint_change(lookup[world, rep, second], endpoint)
                        for rep in replicates
                    ]
                    for world in worlds
                ],
                dtype=np.float64,
            )
            rng = np.random.default_rng(seed + len(weighting))
            equal = mean_intervals(differences, bootstrap_draws, rng, confidence=1 - protocol.alpha)
            world_means: list[float] = []
            for index, world in enumerate(worlds):
                values = differences[index : index + 1]
                intervals = mean_intervals(values, bootstrap_draws, rng, confidence=1 - protocol.alpha)
                q25, q75 = quantile_pair(values.reshape(-1), (0.25, 0.75))
                median, _ = quantile_pair(values.reshape(-1), (0.5, 0.5))
                world_means.append(intervals.mean)
                strata.append(
                    StratumContrast(
                        endpoint,
                        first,
                        second,
                        world,
                        len(replicates),
                        intervals,
                        q25,
                        median,
                        q75,
                        float(np.mean(values > 0)),
                    )
                )
            leave_one_out = (
                [(sum(world_means) - value) / (len(worlds) - 1) for value in world_means]
                if len(worlds) > 1
                else []
            )
            weighting.append(
                WeightingSensitivity(
                    endpoint,
                    first,
                    second,
                    equal,
                    min(world_means),
                    max(world_means),
                    min(leave_one_out) if leave_one_out else None,
                    max(leave_one_out) if leave_one_out else None,
                )
            )
    return HeterogeneityReport(
        tuple(strata),
        tuple(weighting),
        f"Exploratory pointwise {100 * (1 - protocol.alpha):g}% intervals; no adjusted subgroup claim.",
        "Convex and leave-one-stratum-out ranges condition on estimated stratum means; not CIs.",
    )
