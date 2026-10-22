# Copyright (c) 2026 Daniel Ari Friedman
"""Paired simulation contrasts conditional on a fixed grid of world parameters.

Independent simulated agents are resampled within each stratum. Time steps are
never counted as independent observations. Sign-flip inference additionally
requires symmetry/exchangeability of paired differences under its null.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from collections.abc import Sequence

    from thanks_for_nothing.contracts import AgentResult

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.estimation import (
    PairedEstimate,
    StatisticalInputError,
    holm_adjust,
    paired_contrast,
)
from thanks_for_nothing.heterogeneity import HeterogeneityReport, build_heterogeneity
from thanks_for_nothing.outcomes import Endpoint, endpoint_change

Decision = Literal["reject", "retain", "unresolved"]
MINIMUM_REPLICATES: Final = 2
CONDITIONS: Final = (Condition.POSITIVE, Condition.RANDOM, Condition.ABSENCE)


@dataclass(frozen=True, slots=True)
class Contrast:
    """Declared endpoint contrast with simultaneous testing qualification."""

    endpoint: str
    first: str
    second: str
    estimate: PairedEstimate
    holm_p_value: float = 1.0
    holm_mc_low: float = 0.0
    holm_mc_high: float = 1.0
    decision: Decision = "unresolved"


@dataclass(frozen=True, slots=True)
class StatisticalReport:
    """Synthetic study estimands, assumptions, contrasts and controls."""

    schema: str
    seed: int
    estimand: str
    resampling_unit: str
    assumptions: tuple[str, ...]
    contrasts: tuple[Contrast, ...]
    controls: dict[str, bool]
    heterogeneity: HeterogeneityReport


@dataclass(frozen=True, slots=True)
class _PairedDesign:
    lookup: dict[tuple[float, int, Condition], AgentResult]
    luckiness: tuple[float, ...]
    replicates: tuple[int, ...]


def _validate_pair(members: Sequence[AgentResult | None]) -> None:
    """Reject missing or unmatched members of one paired design unit."""
    if any(row is None for row in members):
        msg = "rows"
        raise StatisticalInputError(msg, "missing paired condition")
    present = [row for row in members if row is not None]
    if len({row.exposure_sha256 for row in present}) != 1:
        msg = "rows"
        raise StatisticalInputError(msg, "conditions do not share exogenous exposure")
    if len({row.paired_id for row in present}) != 1:
        msg = "rows"
        raise StatisticalInputError(msg, "paired identifiers differ within a design unit")


def _paired_design(rows: Sequence[AgentResult]) -> _PairedDesign:
    """Admit a complete balanced set of paired exogenous exposures."""
    if not rows:
        msg = "rows"
        raise StatisticalInputError(msg, "complete paired study rows required")
    lookup = {(row.luckiness, row.replicate, row.condition): row for row in rows}
    if len(lookup) != len(rows):
        msg = "rows"
        raise StatisticalInputError(msg, "duplicate agent-condition key")
    luckiness = sorted({row.luckiness for row in rows})
    replicate_sets = [{row.replicate for row in rows if row.luckiness == luck} for luck in luckiness]
    if any(indices != replicate_sets[0] for indices in replicate_sets):
        msg = "rows"
        raise StatisticalInputError(msg, "balanced replicate identifiers required across strata")
    replicates = sorted(replicate_sets[0])
    if len(replicates) < MINIMUM_REPLICATES:
        msg = "rows"
        raise StatisticalInputError(msg, "at least two independent agents per stratum required")
    conditions = {Condition.NO_RECALL, *CONDITIONS}
    if len(rows) != len(luckiness) * len(replicates) * len(conditions):
        msg = "rows"
        raise StatisticalInputError(msg, "a complete four-condition paired design required")
    for luck in luckiness:
        for replicate in replicates:
            members = [lookup.get((luck, replicate, condition)) for condition in conditions]
            _validate_pair(members)
    return _PairedDesign(lookup, tuple(luckiness), tuple(replicates))


def build_statistical_report(
    rows: Sequence[AgentResult],
    *,
    seed: int,
    bootstrap_draws: int,
    permutation_draws: int,
    analysis: AnalysisDesign | None = None,
) -> StatisticalReport:
    """Build eight paired contrasts after admitting complete balanced source rows."""
    protocol = load_analysis() if analysis is None else analysis
    design = _paired_design(rows)
    lookup, luckiness, replicates = design.lookup, design.luckiness, design.replicates
    comparisons = (
        *tuple((condition, Condition.NO_RECALL) for condition in CONDITIONS),
        (Condition.POSITIVE, Condition.RANDOM),
    )
    endpoints: tuple[Endpoint, ...] = (
        "optimism_change",
        "brier_change",
    )
    contrasts: list[Contrast] = []
    family_size = len(comparisons) * len(endpoints)
    for endpoint in endpoints:
        for first, second in comparisons:
            differences = [
                [
                    endpoint_change(lookup[luck, rep, first], endpoint)
                    - endpoint_change(lookup[luck, rep, second], endpoint)
                    for rep in replicates
                ]
                for luck in luckiness
            ]
            estimate = paired_contrast(
                differences,
                seed=seed + len(contrasts),
                bootstrap_draws=bootstrap_draws,
                permutation_draws=permutation_draws,
                family_size=family_size,
                analysis=protocol,
            )
            contrasts.append(Contrast(endpoint, first, second, estimate))
    adjusted = holm_adjust([row.estimate.p_value for row in contrasts])
    lows = holm_adjust([row.estimate.mc_tail_ci_low for row in contrasts])
    highs = holm_adjust([row.estimate.mc_tail_ci_high for row in contrasts])
    qualified: list[Contrast] = []
    for row, p_value, low, high in zip(contrasts, adjusted, lows, highs, strict=True):
        decision: Decision = "unresolved"
        if high < protocol.alpha:
            decision = "reject"
        elif low > protocol.alpha:
            decision = "retain"
        qualified.append(
            replace(row, holm_p_value=p_value, holm_mc_low=low, holm_mc_high=high, decision=decision)
        )
    absence = [row for row in qualified if row.first == "absence_appreciation"]
    return StatisticalReport(
        "thanks_for_nothing.statistics.v2",
        seed,
        "equally weighted fixed-luckiness-grid mean of paired changes",
        "one independently seeded simulated agent, preserving its complete trajectory",
        (
            "Fixed world-parameter grid, not a sampled human population.",
            "Percentile bootstrap resamples paired agents within fixed strata.",
            "Sign-flip null requires symmetric/exchangeable paired differences.",
            f"Holm family contains all {len(qualified)} declared endpoint-by-condition contrasts.",
            f"Monte Carlo intervals have Bonferroni family coverage >={100 * (1 - protocol.alpha):g}%.",
            "Optimism is a declared model readout, not an independently validated human outcome.",
            "Studentized intervals are unavailable if any bootstrap variance vanishes.",
            "World-specific and NLL estimates are exploratory; primary Holm family is unchanged.",
        ),
        tuple(qualified),
        {
            "paired_design_complete": True,
            "shared_world_exposure": True,
            "absence_valuation_preserves_inference": all(
                row.estimate.mean_difference == 0 and row.estimate.p_value == 1 for row in absence
            ),
        },
        build_heterogeneity(
            rows, seed + protocol.heterogeneity_seed_offset, bootstrap_draws, analysis=protocol
        ),
    )


__all__ = [
    "Contrast",
    "PairedEstimate",
    "StatisticalInputError",
    "StatisticalReport",
    "build_statistical_report",
    "holm_adjust",
    "paired_contrast",
]
