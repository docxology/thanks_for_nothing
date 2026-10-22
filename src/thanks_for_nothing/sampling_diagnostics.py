# Copyright (c) 2026 Daniel Ari Friedman
"""Precision diagnostics over whole paired units, conditional on declared model scenarios."""

from dataclasses import dataclass
from math import sqrt

import numpy as np

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.contracts import Condition, ContractError
from thanks_for_nothing.estimation import MATRIX_DIMENSIONS, MINIMUM_REPLICATES
from thanks_for_nothing.gaze_samples import active_samples
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.intervals import quantile_pair


@dataclass(frozen=True, slots=True)
class SamplingPoint:
    """One nested budget, with paired-mean precision and between-unit spread."""

    replicates_per_stratum: int
    strata: int
    mean: float
    monte_carlo_se: float
    q25: float
    median: float
    q75: float
    positive_fraction: float
    empirical_constant: bool


@dataclass(frozen=True, slots=True)
class SamplingCase:
    """A named scientific comparison retaining its own endpoint units."""

    name: str
    contrast: str
    units: str
    points: tuple[SamplingPoint, ...]


@dataclass(frozen=True, slots=True)
class SamplingAudit:
    """Four conditional precision curves with an explicit interpretation boundary."""

    cases: tuple[SamplingCase, ...]
    interpretation: str


def summarize_prefixes(values: FloatArray, analysis: AnalysisDesign) -> tuple[SamplingPoint, ...]:
    """Estimate equal-stratum paired means and MCSE; overlapping prefixes are correlated."""
    if (
        values.ndim != MATRIX_DIMENSIONS
        or min(values.shape) < 1
        or values.shape[1] < MINIMUM_REPLICATES
        or not np.isfinite(values).all()
    ):
        message = "Precision diagnostics require finite paired strata with at least two units"
        raise ContractError(message)
    strata, units = len(values), len(values.T)
    prefixes = sorted({n for n in analysis.diagnostic_prefixes if n <= units} | {units})
    points: list[SamplingPoint] = []
    for count in prefixes:
        selected = values[:, :count]
        low, high = quantile_pair(selected.reshape(-1), (0.25, 0.75))
        median, _ = quantile_pair(selected.reshape(-1), (0.5, 0.5))
        variances = np.asarray(
            np.var(selected - selected[:, :1], axis=1, ddof=1, dtype=np.float64),
            dtype=np.float64,
        )
        variance = float(np.sum(variances / count, dtype=np.float64)) / strata**2
        points.append(
            SamplingPoint(
                count,
                strata,
                float(np.mean(selected, dtype=np.float64)),
                sqrt(variance),
                low,
                median,
                high,
                float(np.mean(selected > 0, dtype=np.float64)),
                float(np.sum(np.abs(selected - selected[:, :1]), dtype=np.float64)) == 0,
            )
        )
    return tuple(points)


def build_sampling_audit(
    bundle: ResearchBundle, analysis: AnalysisDesign | None = None
) -> SamplingAudit:
    """Keep four scientific targets in native units, without treating windows as agents."""
    protocol = load_analysis() if analysis is None else analysis
    study = bundle.study
    indexed = {(r.luckiness, r.replicate, r.condition): r for r in study.rows}
    recall = np.asarray(
        [
            [
                (
                    indexed[world, rep, Condition.POSITIVE].brier_post
                    - indexed[world, rep, Condition.POSITIVE].brier_pre
                )
                - (
                    indexed[world, rep, Condition.RANDOM].brier_post
                    - indexed[world, rep, Condition.RANDOM].brier_pre
                )
                for rep in range(study.design.replicates)
            ]
            for world in study.design.luckiness
        ],
        dtype=np.float64,
    )
    practice = bundle.practice
    context = next(c for c in practice.design.contexts if c.name == "reversal")
    windows = len(context.probabilities)
    pi = {(r.context, r.replicate, r.window, r.condition): r for r in practice.rows}
    enactment = np.asarray(
        [
            [
                np.mean(
                    [
                        pi[context.name, rep, window, "inquiry"].heldout_log_loss
                        - pi[context.name, rep, window, "rigid"].heldout_log_loss
                        for window in range(windows)
                    ]
                )
                for rep in range(practice.design.replicates)
            ]
        ],
        dtype=np.float64,
    )
    active = next(
        sample.values
        for sample in active_samples(bundle.gaze.episodes, bundle.gaze.design)
        if sample.identity
        == ("active", "reversal", "inquiry_open", "pragmatic_open", "mean_balanced_log_loss")
    )
    boundary = bundle.boundary_gaze
    encoding = max(r.boundary for r in boundary.episodes)
    bi = {
        (r.scene, r.replicate, r.condition): r
        for r in boundary.episodes
        if r.regime == "diagnostic" and r.boundary == encoding
    }
    scenes = sorted({scene for scene, _, _ in bi})
    anchored = np.asarray(
        [
            [
                bi[scene, rep, "integrated"].anchored_regret - bi[scene, rep, "visual"].anchored_regret
                for rep in range(boundary.design.replicates)
            ]
            for scene in scenes
        ],
        dtype=np.float64,
    )
    return SamplingAudit(
        (
            SamplingCase(
                "Recall", "Positive minus random", "Brier loss", summarize_prefixes(recall, protocol)
            ),
            SamplingCase(
                "Practice: reversal",
                "Inquiry minus rigid",
                "Nats / observation",
                summarize_prefixes(enactment, protocol),
            ),
            SamplingCase(
                "Gaze: reversal",
                "Inquiry minus open utility",
                "Nats / outcome",
                summarize_prefixes(active, protocol),
            ),
            SamplingCase(
                f"Encoding H{encoding}",
                "Integrated minus visual",
                "Anchor nats / outcome",
                summarize_prefixes(anchored, protocol),
            ),
        ),
        "Correlated prefixes estimate fixed-model Monte Carlo error, not human or model uncertainty.",
    )
