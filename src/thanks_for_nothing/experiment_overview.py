# Copyright (c) 2026 Daniel Ari Friedman
"""One experimental-question registry for the overview figure and technical crosswalk."""

from dataclasses import dataclass
from pathlib import Path
from textwrap import fill

from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, save


@dataclass(frozen=True, slots=True)
class ExperimentQuestion:
    """An experimental contrast, assessment and falsifying control considered together."""

    question: str
    manipulation: str
    assessment: str
    control: str


def experiment_questions(bundle: ResearchBundle) -> tuple[ExperimentQuestion, ...]:
    """Read budgets and independent units from the actual admitted experiment records."""
    study, practice, gaze, boundary = (
        bundle.study.design,
        bundle.practice.design,
        bundle.gaze.design,
        bundle.boundary_gaze.design,
    )
    units = len({row.paired_id for row in bundle.study.rows})
    practice_n = practice.replicates
    return (
        ExperimentQuestion(
            "Recall: does selected replay improve prediction?",
            "Positive vs random replay; same exposure and matched replay dose.",
            f"{study.replicates} paired units/world; frozen Brier and optimism tests.",
            "Value-only control: unchanged beliefs and predictive losses.",
        ),
        ExperimentQuestion(
            "Absence: no event, no record, or a different value?",
            "Functioning detector vs missing record; actual vs reference cost.",
            "Posterior change in bits; separate counterfactual cost value.",
            "No record adds no evidence under the declared rule.",
        ),
        ExperimentQuestion(
            "Practice: does chosen activity provide usable access?",
            f"Value and cost affect activity; {practice.calibration_samples} calibration observations.",
            f"{practice.assessment_samples} new outcomes/window; {practice_n} paired units/context.",
            "Sham or blocked access: activity can cost without revising.",
        ),
        ExperimentQuestion(
            "Transfer: what follows from a learned likelihood?",
            "Freeze learned channels; compare likelihood and readout bridges.",
            f"{units} complete paired agents; attention and scene loss separately.",
            "A favorable attention shift need not improve prediction.",
        ),
        ExperimentQuestion(
            "Scene inquiry: access or the sampling policy?",
            f"Restricted vs open; utility vs inquiry vs uniform; {gaze.steps} decisions.",
            f"{gaze.replicates} paired units/context; scene loss and movement cost.",
            "Already-open comparators test an inquiry-specific increment.",
        ),
        ExperimentQuestion(
            "Boundary inquiry: can the inferred frame be used?",
            f"Spatial vs action-response queries; one {boundary.steps}-decision budget.",
            f"{boundary.replicates} paired units/cell; encoding and reference losses.",
            "Label-only, excluded support and matched-query erasure controls.",
        ),
    )


def experiment_logic_table(bundle: ResearchBundle) -> str:
    """Give the overview's exact task descriptions a searchable textual counterpart."""
    rows = [
        "| Experimental question | Manipulation / matched input | Assessment | Control / limit |",
        "| --- | --- | --- | --- |",
    ]
    rows.extend(
        f"| {row.question} | {row.manipulation} | {row.assessment} | {row.control} |"
        for row in experiment_questions(bundle)
    )
    return "\n".join(rows)


def experiment_overview(bundle: ResearchBundle, output: Path) -> FigureRecord:
    """Show the manipulation, independent assessment and interpretation test for each task."""
    fig, axis = figure(6.54, 8.1, automatic_layout=False)
    fig.subplots_adjust(left=0.035, right=0.985, top=0.985, bottom=0.025)
    _ = axis.set(xlim=(0, 1), ylim=(0, 1))
    _ = axis.axis("off")
    columns = (
        (0.01, "Manipulate / match", "no_recall"),
        (0.35, "Assess after choice", "positive_recall"),
        (0.69, "Control / limit", "harm"),
    )
    for x, title, role in columns:
        _ = axis.text(x, 0.985, title, fontsize=10.5, weight="bold", color=PALETTE[role])
    for index, row in enumerate(experiment_questions(bundle)):
        y = 0.935 - index * 0.151
        _ = axis.text(
            0.01,
            y,
            f"{chr(ord('a') + index)}  {row.question}",
            fontsize=11,
            weight="bold",
            va="top",
            color=PALETTE["ink"],
        )
        _ = axis.plot([0.01, 0.99], [y - 0.025] * 2, color=PALETTE["grid"])
        for (x, _, role), text in zip(
            columns, (row.manipulation, row.assessment, row.control), strict=True
        ):
            _ = axis.text(
                x,
                y - 0.043,
                fill(text, 24),
                fontsize=10.5,
                va="top",
                linespacing=1.35,
                color=PALETTE[role],
            )
    return save(
        fig,
        output,
        "experiment_overview",
        "Experimental questions, comparisons and assessment targets",
        "Each task pairs a controlled change with an independent target and an interpretation test.",
        (
            "data/study.json",
            "data/nothingness.json",
            "data/emptiness_practice.json",
            "data/gaze.json",
            "data/boundary_gaze.json",
        ),
    )
