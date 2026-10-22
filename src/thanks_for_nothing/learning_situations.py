# Copyright (c) 2026 Daniel Ari Friedman
"""Situated recall and enacted-inquiry results from unchanged admitted experiments."""

from pathlib import Path

import numpy as np
from matplotlib.ticker import MaxNLocator

from thanks_for_nothing.concepts import COUNTERFACTUAL_VALUE, NON_REIFICATION
from thanks_for_nothing.contracts import Condition, StudyResult
from thanks_for_nothing.practice_contracts import PracticeAudit
from thanks_for_nothing.situation_drawing import (
    SituationLink,
    SituationNode,
    diagram_note,
    draw_link,
    draw_node,
    situation_canvas,
)
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.visual_style import LABELS, PALETTE, FigureRecord, save
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE, PRACTICE_LABELS, PRACTICE_ROLES


def recall_situation(study: StudyResult, report: StatisticalReport, output: Path) -> FigureRecord:
    """Place world-specific paired changes beside their observation, replay, and assessment task."""
    fig, setting, optimism, brier = situation_canvas(
        "Paired experience, replay, and a new test",
        "Test: does selected replay improve the model's independent predictions?",
    )
    design = study.design
    for node in (
        SituationNode((0.10, 0.77), "World\np", "ink", "world"),
        SituationNode((0.36, 0.77), "Observed\nevents"),
        SituationNode((0.63, 0.77), "Agent\nq(well)", "positive_recall", "belief"),
        SituationNode((0.90, 0.77), "Score new\noutcomes"),
        SituationNode((0.63, 0.30), "Replay\ncontent", "matched_random_recall"),
    ):
        draw_node(setting, node)
    for start, end in (
        ((0.19, 0.77), (0.25, 0.77)),
        ((0.46, 0.77), (0.51, 0.77)),
        ((0.75, 0.77), (0.79, 0.77)),
        ((0.63, 0.42), (0.63, 0.64)),
    ):
        draw_link(setting, SituationLink(start, end))
    diagram_note(setting, (0.26, 0.47), "Same exposure\nwithin a paired unit")
    diagram_note(setting, (0.87, 0.30), "Positive / random\nmatched dose")
    diagram_note(setting, (0.27, 0.18), f"{COUNTERFACTUAL_VALUE.label}\nValue without belief learning")
    diagram_note(
        setting,
        (0.50, -0.01),
        "\n".join(
            (
                f"{design.replicates} independent paired units / world",
                "; ".join(
                    (
                        f"Optimism test: {design.assessment_trials} trials",
                        f"Loss test: {design.evaluation_trials} trials",
                    )
                ),
            )
        ),
    )
    for axis, endpoint, title, ylabel in (
        (
            optimism,
            "optimism_change",
            "b  Optimism readout",
            f"Paired change contrast x {DISPLAY_SCALE:g}",
        ),
        (brier, "brier_change", "c  Predictive Brier loss", f"Paired loss contrast x {DISPLAY_SCALE:g}"),
    ):
        _ = axis.axhline(0, color=PALETTE["ink"], lw=1)
        for reference, marker in ((Condition.NO_RECALL, "o-"), (Condition.RANDOM, "s--")):
            rows = [
                r
                for r in report.heterogeneity.strata
                if r.endpoint == endpoint and r.second == reference
            ]
            means = [DISPLAY_SCALE * r.intervals.mean for r in rows]
            _ = axis.errorbar(
                [r.world for r in rows],
                means,
                yerr=[
                    [DISPLAY_SCALE * (r.intervals.mean - r.intervals.analytic_low) for r in rows],
                    [DISPLAY_SCALE * (r.intervals.analytic_high - r.intervals.mean) for r in rows],
                ],
                fmt=marker,
                capsize=3,
                color=PALETTE[reference],
                label=f"Positive minus {LABELS[reference].lower()}",
            )
        _ = axis.set(title=title, xlabel="World P(well)", ylabel=ylabel)
        _ = axis.set_xticks(design.luckiness, [f"{p:g}" for p in design.luckiness])
    return save(
        fig,
        output,
        "recall_situation",
        "From shared experience to distinct readouts",
        "Shared exposure and replay, with world-specific paired optimism and Brier changes.",
        ("data/study.json", "data/statistics.json", "data/concepts.json"),
    )


def practice_situation(audit: PracticeAudit, output: Path) -> FigureRecord:
    """Connect costly access and evidence-based family choice to independent prediction."""
    design = audit.design
    fig, setting, forecasts, contrasts = situation_canvas(
        "Practice changes access to a predictor",
        "Test: can costly activity expose a useful alternative before assessment?",
    )
    for node in (
        SituationNode((0.10, 0.78), "Process\np(t)", "ink", "world"),
        SituationNode((0.36, 0.78), f"Calibrate\nn={design.calibration_samples}"),
        SituationNode((0.64, 0.78), "Retain /\nrevise", "positive_recall", "belief"),
        SituationNode((0.90, 0.78), f"New test\nn={design.assessment_samples}"),
        SituationNode(
            (0.10, 0.28), f"Value inquiry\n{design.examinability_preference:g}", NON_REIFICATION.role
        ),
        SituationNode((0.36, 0.28), f"Activity\ncost {design.practice_cost:g}", "matched_random_recall"),
        SituationNode((0.64, 0.28), "Alternative\navailable?", "positive_recall"),
    ):
        draw_node(setting, node)
    for start, end in (
        ((0.19, 0.78), (0.25, 0.78)),
        ((0.46, 0.78), (0.52, 0.78)),
        ((0.76, 0.78), (0.79, 0.78)),
        ((0.20, 0.28), (0.25, 0.28)),
        ((0.46, 0.28), (0.53, 0.28)),
        ((0.64, 0.40), (0.64, 0.64)),
    ):
        draw_link(setting, SituationLink(start, end))
    diagram_note(setting, (0.89, 0.28), "Sham / no access:\nactivity ≠ access")
    diagram_note(
        setting,
        (0.50, -0.01),
        "\n".join(
            (
                f"{NON_REIFICATION.label}: a finite enabling model",
                f"{design.replicates} paired units / context; realization is unmeasured",
            )
        ),
    )
    context = next(c for c in design.contexts if c.name == "reversal")
    windows = list(range(1, len(context.probabilities) + 1))
    _ = forecasts.plot(windows, context.probabilities, ":", color=PALETTE["ink"], label="Process")
    for condition, marker in (("rigid", "s-"), ("inquiry", "o-"), ("no_preference", "^--")):
        means = [
            float(
                np.mean(
                    [
                        r.forecast
                        for r in audit.rows
                        if r.context == context.name and r.condition == condition and r.window == w - 1
                    ]
                )
            )
            for w in windows
        ]
        _ = forecasts.plot(
            windows,
            means,
            marker,
            color=PALETTE[PRACTICE_ROLES[condition]],
            label=PRACTICE_LABELS[condition],
        )
    _ = forecasts.set(
        title="b  Reversal: frozen forecasts", xlabel="Window", ylabel="P(channel 0)", ylim=(0, 1)
    )
    forecasts.xaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    rows = [r for r in audit.contrasts if r.context == "reversal"]
    _ = contrasts.axvline(0, color=PALETTE["ink"], lw=1)
    for index, row in enumerate(rows):
        interval = row.heldout_loss_difference
        _ = contrasts.errorbar(
            [interval.mean],
            [index],
            xerr=[[interval.mean - interval.analytic_low], [interval.analytic_high - interval.mean]],
            fmt="o",
            capsize=3,
            color=PALETTE[PRACTICE_ROLES[row.condition]],
            label=PRACTICE_LABELS[row.condition],
        )
    _ = contrasts.set_yticks(list(range(len(rows))), [PRACTICE_LABELS[r.condition] for r in rows])
    _ = contrasts.set(
        title="c  Reversal: held-out loss",
        xlabel="Minus rigid\n(nats / observation)",
        ylim=(len(rows) - 0.4, -0.6),
    )
    contrasts.xaxis.set_major_locator(MaxNLocator(nbins=3))
    return save(
        fig,
        output,
        "practice_situation",
        "Activity, access, and the test of a working representation",
        "Costly access, reversal forecasts and policy loss, including sham and blocked access.",
        ("data/emptiness_practice.json", "data/concepts.json"),
    )
