# Copyright (c) 2026 Daniel Ari Friedman
"""Paired finite study with unchanged exogenous worlds and independent scoring."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import assert_never

import numpy as np

from thanks_for_nothing.contracts import (
    AgentResult,
    Condition,
    DailyTrace,
    Design,
    LearnedChannel,
    LearningExperiment,
    StudyControls,
    StudyDesign,
    StudyResult,
)
from thanks_for_nothing.inference import (
    FloatArray,
    IntArray,
    cumulative,
    frozen_likelihood,
    learn,
    normalize_counts,
    optimism,
    posterior,
    score,
)
from thanks_for_nothing.specifications import Tensors, load_study
from thanks_for_nothing.standalone_gnn import ModelContext, standalone_model


@dataclass(frozen=True, slots=True)
class Day:
    """Updated pseudocounts and online beliefs for a single day."""

    counts: FloatArray
    mean_well: float
    recalled: int


def train_day(  # noqa: PLR0913, PLR0917 - Explicit numerical inputs define this training primitive.
    counts: FloatArray,
    observations: IntArray,
    prior: FloatArray,
    transition: FloatArray,
    design: Design,
    condition: Condition,
    recall_rng: np.random.Generator,
) -> Day:
    """Learn observations, then replay only existing events using stored event priors."""
    beliefs: list[float] = []
    priors: list[FloatArray] = []
    q = prior.copy()
    for index in range(observations.size):
        observation = int(np.sum(observations[index : index + 1]))
        p = prior if index == 0 else transition @ q
        priors.append(p)
        q = posterior(normalize_counts(counts), p, int(observation))
        beliefs.append(float(np.sum(q[:1])))
        counts = learn(counts, int(observation), q, design.learning_rate, design.forgetting)
    positive = [i for i in range(observations.size) if np.sum(observations[i : i + 1]) == 0]
    dose = min(design.recall_count, len(positive))
    match condition:
        case Condition.NO_RECALL | Condition.ABSENCE:
            selected: list[int] = []
        case Condition.POSITIVE:
            selected = sorted(positive, key=lambda _: float(recall_rng.random()))[:dose]
        case Condition.RANDOM:
            selected = sorted(range(observations.size), key=lambda _: float(recall_rng.random()))[:dose]
        case _:
            assert_never(condition)
    for index in sorted(selected):
        obs = int(np.sum(observations[index : index + 1]))
        q_recall = posterior(
            normalize_counts(counts), priors[index], obs, precision=design.recall_precision
        )
        counts = learn(counts, obs, q_recall, design.learning_rate, design.forgetting)
    return Day(counts, float(np.mean(beliefs)), len(selected))


def sample_world(
    rng: np.random.Generator, luckiness: float, likelihood: FloatArray, size: int
) -> tuple[IntArray, IntArray]:
    """Independent world states: each transition column equals [luck,1-luck]."""
    states = (rng.random(size) >= luckiness).astype(np.int64)
    uniforms = rng.random(size)
    thresholds = cumulative(likelihood.take(states, axis=1), axis=0)
    observations = np.asarray(
        np.sum(uniforms[None, :] > thresholds, axis=0, dtype=np.int64), dtype=np.int64
    )
    return states, observations


def run_learning_experiment(  # noqa: PLR0915 - One bounded paired experimental orchestration.
    *, replicates: int | None = None, seed: int | None = None, specification_dir: Path | None = None
) -> LearningExperiment:
    """Run the GNN-declared paired study without writing output files."""
    model, admitted = load_study(specification_dir)
    changes = admitted.model_dump()
    if replicates is not None:
        changes["replicates"] = replicates
    if seed is not None:
        changes["seed"] = seed
    design = Design.model_validate(changes)
    likelihood = np.asarray(model.tensors.A, dtype=np.float64)
    prior = np.asarray(model.tensors.D, dtype=np.float64)
    transition = np.asarray(model.tensors.B, dtype=np.float64)[:, :, 0]
    news = tuple(
        standalone_model(
            f"optimism_{name}",
            Tensors.model_validate(
                {
                    "A": channel,
                    "B": model.tensors.B,
                    "C": np.zeros(len(channel), dtype=np.float64),
                    "D": model.tensors.D,
                }
            ),
            context=ModelContext(
                (model,),
                "thanks_for_nothing.inference:optimism",
                f"News A for {name} mode. Trial priors enter from the assessment design.",
            ),
        )
        for name, channel in (("well", design.optimism_well), ("poor", design.optimism_poor))
    )
    well, poor = (np.asarray(item.tensors.A, dtype=np.float64) for item in news)
    rows: list[AgentResult] = []
    parameters: list[LearnedChannel] = []
    traces: list[DailyTrace] = []
    total_days = design.baseline_days + design.intervention_days
    for stratum, luck in enumerate(design.luckiness):
        world_prior = np.asarray([luck, 1 - luck], dtype=np.float64)
        world = standalone_model(
            "recall_world",
            model.tensors.model_copy(
                update={
                    "D": tuple(world_prior),
                    "B": Tensors.model_validate(
                        {
                            "A": model.tensors.A,
                            "B": np.repeat(world_prior[:, None, None], len(world_prior), axis=1),
                            "C": model.tensors.C,
                            "D": world_prior,
                        }
                    ).B,
                }
            ),
            context=ModelContext(
                (model,),
                "thanks_for_nothing.experiments:sample_world",
                "IID exogenous states: every B column equals D. Paired conditions share A.",
            ),
        )
        world_likelihood = np.asarray(world.tensors.A, dtype=np.float64)
        world_probability = world.tensors.D[0]
        for replicate in range(design.replicates):
            streams = np.random.SeedSequence([design.seed, stratum, replicate]).spawn(4)
            world_rng, eval_rng, task_rng = (np.random.default_rng(s) for s in streams[:3])
            states, observations = sample_world(
                world_rng, world_probability, world_likelihood, total_days * design.steps_per_day
            )
            eval_states, eval_obs = sample_world(
                eval_rng, world_probability, world_likelihood, design.evaluation_trials
            )
            trial_priors = task_rng.uniform(
                design.task_prior_min, design.task_prior_max, design.assessment_trials
            )
            exposure = sha256(states.tobytes() + observations.tobytes()).hexdigest()
            daily = observations.reshape(total_days, design.steps_per_day)
            baseline = likelihood * design.prior_concentration
            baseline_trace: list[float] = []
            for day_index in range(design.baseline_days):
                day = daily[day_index : day_index + 1].reshape(-1)
                result = train_day(
                    baseline, day, prior, transition, design, Condition.NO_RECALL, world_rng
                )
                baseline = result.counts
                baseline_trace.append(result.mean_well)
            pre = score(normalize_counts(baseline), prior, eval_obs, eval_states)
            opt_pre = optimism(pre.world_well, trial_priors, well, poor)
            for condition in Condition:
                counts = baseline.copy()
                recall_rng = np.random.default_rng(streams[3])
                recall_counts: list[int] = []
                condition_trace = list(baseline_trace)
                for day_index in range(design.baseline_days, total_days):
                    day = daily[day_index : day_index + 1].reshape(-1)
                    result = train_day(counts, day, prior, transition, design, condition, recall_rng)
                    counts = result.counts
                    recall_counts.append(result.recalled)
                    condition_trace.append(result.mean_well)
                parameters.append(
                    LearnedChannel(
                        condition,
                        luck,
                        replicate,
                        f"{stratum}:{replicate}",
                        exposure,
                        frozen_likelihood(baseline),
                        frozen_likelihood(counts),
                    )
                )
                post = score(normalize_counts(counts), prior, eval_obs, eval_states)
                appreciation = 0.0
                match condition:
                    case Condition.ABSENCE:
                        appreciation = float(
                            np.mean(abs(daily[design.baseline_days :] - 1) <= 0)
                            * design.reference_hazard
                            * design.harm_cost
                        )
                    case Condition.NO_RECALL | Condition.POSITIVE | Condition.RANDOM:
                        pass
                    case _:
                        assert_never(condition)
                rows.append(
                    AgentResult(
                        condition,
                        luck,
                        replicate,
                        f"{stratum}:{replicate}",
                        pre.world_well,
                        post.world_well,
                        pre.brier,
                        post.brier,
                        pre.nll,
                        post.nll,
                        post.entropy,
                        opt_pre,
                        optimism(post.world_well, trial_priors, well, poor),
                        appreciation,
                        float(np.mean(recall_counts)),
                        exposure,
                    )
                )
                traces.extend(
                    DailyTrace(condition, luck, replicate, i + 1, mean)
                    for i, mean in enumerate(condition_trace)
                )
    groups = [rows[i : i + len(Condition)] for i in range(0, len(rows), len(Condition))]
    controls: StudyControls = {
        "identical_exposures": all(len({r.exposure_sha256 for r in group}) == 1 for group in groups),
        "identical_baselines": all(
            len({(r.pre_world_well, r.brier_pre, r.nll_pre, r.optimism_pre) for r in group}) == 1
            for group in groups
        ),
        "absence_belief_null": all(
            (g[0].post_world_well, g[0].brier_post, g[0].nll_post, g[0].optimism_post)
            == (g[3].post_world_well, g[3].brier_post, g[3].nll_post, g[3].optimism_post)
            for g in groups
        ),
        "dose_matched": all(g[1].mean_recall_count == g[2].mean_recall_count for g in groups),
    }
    study = StudyResult(
        StudyDesign(
            seed=design.seed,
            replicates=design.replicates,
            luckiness=design.luckiness,
            baseline_days=design.baseline_days,
            intervention_days=design.intervention_days,
            steps_per_day=design.steps_per_day,
            recall_count=design.recall_count,
            recall_precision=design.recall_precision,
            learning_rate=design.learning_rate,
            forgetting=design.forgetting,
            prior_concentration=design.prior_concentration,
            bootstrap_draws=design.bootstrap_draws,
            permutation_draws=design.permutation_draws,
            assessment_trials=design.assessment_trials,
            task_prior_min=design.task_prior_min,
            task_prior_max=design.task_prior_max,
            sensitivity_replicates=design.sensitivity_replicates,
            sensitivity_prior_concentrations=design.sensitivity_prior_concentrations,
            sensitivity_recall_precisions=design.sensitivity_recall_precisions,
            calibration_replicates=design.calibration_replicates,
            calibration_sample_size=design.calibration_sample_size,
            calibration_bootstrap_draws=design.calibration_bootstrap_draws,
            calibration_permutation_draws=design.calibration_permutation_draws,
            evaluation_trials=design.evaluation_trials,
            reference_hazard=design.reference_hazard,
            harm_cost=design.harm_cost,
            optimism_well=design.optimism_well,
            optimism_poor=design.optimism_poor,
        ),
        tuple(rows),
        tuple(traces),
        controls,
        model.source_hash,
    )
    return LearningExperiment(study, tuple(parameters))


def run_study(
    *,
    replicates: int | None = None,
    seed: int | None = None,
    specification_dir: Path | None = None,
) -> StudyResult:
    """Retain the original public study result while the training experiment also exposes its models."""
    return run_learning_experiment(
        replicates=replicates, seed=seed, specification_dir=specification_dir
    ).study
