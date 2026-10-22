# Copyright (c) 2026 Daniel Ari Friedman
"""Repeated, costly inquiry with independent calibration and assessment observations."""

from hashlib import sha256
from math import log, log1p
from pathlib import Path

import numpy as np

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.intervals import mean_intervals
from thanks_for_nothing.practice_contracts import (
    Condition,
    PracticeAudit,
    PracticeContrast,
    PracticeDesign,
    PracticeRow,
)
from thanks_for_nothing.practice_controls import practice_controls
from thanks_for_nothing.practice_inference import admitted_priors, compare_priors, practice_probability
from thanks_for_nothing.specifications import Tensors, load_model
from thanks_for_nothing.standalone_gnn import ModelContext, standalone_model


def _validate_design(design: PracticeDesign) -> None:
    if (
        len({c.name for c in design.contexts}) != len(design.contexts)
        or {c.name for c in design.contexts} != {"stationary", "reversal"}
        or set(design.conditions) != {"rigid", "inquiry", "no_preference", "sham", "no_access"}
        or len(set(design.conditions)) != len(design.conditions)
        or any(not np.isfinite(p) or not 0 < p < 1 for c in design.contexts for p in c.probabilities)
        or len({len(c.probabilities) for c in design.contexts}) != 1
    ):
        message = "Practice requires unique contexts, five conditions and valid equal-length schedules"
        raise ContractError(message)


def _rows(design: PracticeDesign, model_dir: Path | None) -> tuple[PracticeRow, ...]:
    model = load_model("emptiness_practice", model_dir)
    restricted, open_prior = admitted_priors(model, design)
    likelihood = np.asarray(model.tensors.A, dtype=np.float64)
    rows: list[PracticeRow] = []
    for context_index, context in enumerate(design.contexts):
        stages = len(context.probabilities)
        process = standalone_model(
            "practice_process",
            Tensors.model_validate(
                {
                    "A": [context.probabilities, tuple(1 - p for p in context.probabilities)],
                    "B": np.asarray(
                        [
                            [[float(n == min(p + 1, stages - 1))] for p in range(stages)]
                            for n in range(stages)
                        ]
                    ),
                    "C": np.zeros(len(model.tensors.C)),
                    "D": np.eye(stages)[0],
                }
            ),
            context=ModelContext(
                (model,),
                "thanks_for_nothing.emptiness_practice:_rows",
                f"Exogenous {context.name} Bernoulli schedule; known stage, absorbing last stage.",
            ),
        )
        probabilities = process.tensors.A[0]
        for replicate in range(design.replicates):
            streams = np.random.SeedSequence([design.seed, context_index, replicate]).spawn(4)
            calibration_rng, assessment_rng, action_rng, access_rng = (
                np.random.default_rng(stream) for stream in streams
            )
            state: dict[Condition, tuple[bool, float]] = dict.fromkeys(design.conditions, (False, 0.0))
            for window, probability in enumerate(probabilities):
                calibration = calibration_rng.random(design.calibration_samples) < probability
                assessment = assessment_rng.random(design.assessment_samples) < probability
                n_calibration = int(np.sum(calibration, dtype=np.int64))
                n_assessment = int(np.sum(assessment, dtype=np.int64))
                digest = sha256(calibration.tobytes() + assessment.tobytes()).hexdigest()
                comparison = compare_priors(
                    likelihood,
                    restricted,
                    open_prior,
                    (n_calibration, design.calibration_samples - n_calibration),
                )
                action_uniform, access_uniform = float(action_rng.random()), float(access_rng.random())
                for condition in design.conditions:
                    uses_open, previous_gain = state[condition]
                    preference = 0.0 if condition == "no_preference" else design.examinability_preference
                    action_probability = (
                        0.0
                        if condition == "rigid"
                        else practice_probability(design, preference, previous_gain)
                    )
                    practiced = action_uniform < action_probability
                    access = (
                        practiced
                        and condition not in {"sham", "no_access"}
                        and access_uniform < design.metacognitive_access
                    )
                    if access:
                        uses_open = comparison.prefers_open
                    forecast = comparison.open_forecast if uses_open else comparison.restricted_forecast
                    loss = (
                        -(
                            n_assessment * log(forecast)
                            + (design.assessment_samples - n_assessment) * log1p(-forecast)
                        )
                        / design.assessment_samples
                    )
                    rows.append(
                        PracticeRow(
                            context.name,
                            replicate,
                            window,
                            condition,
                            probability,
                            n_calibration,
                            n_assessment,
                            digest,
                            action_probability,
                            practiced,
                            access,
                            previous_gain,
                            uses_open,
                            forecast,
                            float(loss),
                            design.practice_cost if practiced else 0.0,
                            comparison,
                        )
                    )
                    state[condition] = (
                        uses_open,
                        max(0.0, comparison.log_bayes_factor) if access else previous_gain,
                    )
    return tuple(rows)


def practice_contrasts(
    rows: tuple[PracticeRow, ...], design: PracticeDesign, analysis: AnalysisDesign
) -> tuple[PracticeContrast, ...]:
    """Recompute paired held-out inference from retained whole-agent records."""
    indexed = {(row.context, row.condition, row.replicate, row.window): row for row in rows}
    output: list[PracticeContrast] = []
    rng = np.random.default_rng(np.random.SeedSequence([design.seed, 1]))
    for context in design.contexts:
        for condition in design.conditions:
            if condition == "rigid":
                continue
            selected = [
                row for row in rows if row.context == context.name and row.condition == condition
            ]
            units = [
                float(
                    np.mean(
                        [
                            indexed[context.name, condition, replicate, window].heldout_log_loss
                            - indexed[context.name, "rigid", replicate, window].heldout_log_loss
                            for window in range(len(context.probabilities))
                        ]
                    )
                )
                for replicate in range(design.replicates)
            ]
            intervals = mean_intervals(
                np.asarray([units], dtype=np.float64),
                design.bootstrap_draws,
                rng,
                confidence=1 - analysis.alpha,
            )
            output.append(
                PracticeContrast(
                    context.name,
                    condition,
                    intervals,
                    float(np.mean([r.practiced for r in selected])),
                    float(np.mean([r.effective_access for r in selected])),
                    float(np.mean([r.incurred_cost for r in selected])),
                )
            )
    return tuple(output)


def build_practice_audit(
    *,
    specification_dir: Path | None = None,
    replicates: int | None = None,
) -> PracticeAudit:
    """Keep extension results distinct from the original eight primary contrasts."""
    model = load_model("emptiness_practice", specification_dir)
    design = PracticeDesign.model_validate_json(model.parameters_json)
    if replicates is not None:
        design = PracticeDesign.model_validate(design.model_dump() | {"replicates": replicates})
    _validate_design(design)
    _ = admitted_priors(model, design)
    rows = _rows(design, specification_dir)
    controls = practice_controls(model, design, rows)
    return PracticeAudit(
        "thanks_for_nothing.emptiness_practice.v1",
        design,
        model.source_hash,
        rows,
        practice_contrasts(rows, design, load_analysis(specification_dir)),
        controls,
        all(controls.values()),
    )
