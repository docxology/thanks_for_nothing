# Copyright (c) 2026 Daniel Ari Friedman
"""Render finite semantic, attention and sensitivity comparisons at paper width."""

from pathlib import Path
from typing import Final

import numpy as np
from numpy.typing import NDArray  # noqa: TC002 - Numerical local annotation.

from thanks_for_nothing.attention import AttentionAudit
from thanks_for_nothing.calibration import CalibrationAudit
from thanks_for_nothing.calibration_figures import statistical_calibration
from thanks_for_nothing.concept_figures import concept_map
from thanks_for_nothing.concepts import MISSING_OBSERVATION, OBSERVED_ABSENCE
from thanks_for_nothing.contracts import StudyResult
from thanks_for_nothing.diagnostic_figures import paired_spread, weighting_sensitivity
from thanks_for_nothing.nothingness import NothingnessAudit
from thanks_for_nothing.sensitivity import SensitivityAudit
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.study_figures import (
    appreciation_null,
    calibration_by_world,
    paired_contrasts,
)
from thanks_for_nothing.trajectory_figures import trajectories
from thanks_for_nothing.visual_style import (
    DIVERGING_CMAP,
    PALETTE,
    FigureRecord,
    color_scale,
    figure,
    panels,
    save,
)
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE

LABEL_MIDPOINT: Final = 0.5


def absence_information(audit: NothingnessAudit, output: Path) -> FigureRecord:
    """Separate posterior probabilities from the magnitude of an information update."""
    fig, _ = figure(6.54, 3.8)
    fig.clear()
    left, right = panels(fig)
    probabilities = (audit.prior[0], audit.missing_posterior[0], audit.observed_absence_posterior[0])
    for index, (value, role) in enumerate(
        zip(probabilities, ("no_recall", MISSING_OBSERVATION.role, OBSERVED_ABSENCE.role), strict=True)
    ):
        _ = left.bar([index], [value], width=0.55, color=PALETTE[role])
        _ = left.text(index, value + 0.035, f"{value:.3f}", fontsize=10, ha="center")
    labels = ["Missing\nrecord", "Observed\nabsence"]
    _ = left.set_xticks([0, 1, 2], ["Prior", *labels])
    _ = left.set(ylim=(0, 1), ylabel="P(low hazard)", title="State belief")
    information = (audit.missing_kl_bits, audit.observed_absence_kl_bits)
    for index, (value, role) in enumerate(
        zip(information, (MISSING_OBSERVATION.role, OBSERVED_ABSENCE.role), strict=True)
    ):
        _ = right.bar([index], [value], width=0.55, color=PALETTE[role])
        _ = right.text(index, value + max(information) * 0.07, f"{value:.3f}", fontsize=10, ha="center")
    _ = right.set_xticks([0, 1], labels)
    _ = right.set(
        ylim=(0, max(max(information) * 1.35, 0.05)),
        ylabel="KL(posterior || prior), bits",
        title="Information update",
    )
    return save(
        fig,
        output,
        "absence_information",
        "Absence and missingness differ",
        "A finite absence observation updates belief; missingness preserves the prior by convention.",
        ("data/concepts.json", "data/nothingness.json"),
    )


def attention_policies(audit: AttentionAudit, output: Path) -> FigureRecord:
    """Compare all category probabilities, including small masses, without color-only identity."""
    fig, ax = figure(6.54, 3.8)
    for index, values in enumerate(
        (
            [r.negative_mass for r in audit.rows],
            [r.neutral_mass for r in audit.rows],
            [r.positive_mass for r in audit.rows],
        )
    ):
        _ = ax.plot([100 * value for value in values], [index] * len(values), color=PALETTE["grid"])
        for profile, (row, value, marker, role) in enumerate(
            zip(audit.rows, values, ("o", "s"), ("positive_recall", "harm"), strict=True)
        ):
            _ = ax.plot(
                [100 * value],
                [index],
                marker,
                color=PALETTE[role],
                label=row.condition.replace("attention_", "").capitalize() + " precision"
                if index == 0
                else "_nolegend_",
            )
            _ = ax.text(
                100 * value,
                index + (0.15 if profile == 0 else -0.15),
                f"{100 * value:.2f}%",
                fontsize=10,
                ha="right" if value > LABEL_MIDPOINT else "left",
                va="center",
            )
        _ = ax.set_yticks([0, 1, 2], ["Negative", "Neutral", "Positive"])
    _ = ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    _ = ax.set(
        xlim=(-2, 102),
        ylim=(-0.5, 2.9),
        xlabel="Mean policy probability mass",
        title="Fixed process; exogenous precision",
    )
    _ = ax.legend(ncol=2, loc="upper center")
    return save(
        fig,
        output,
        "attention_policies",
        "Fixed-process policy comparison",
        "All masses are labeled; profile markers differ. Connectors are not intervals.",
        ("data/attention.json",),
    )


def sensitivity(audit: SensitivityAudit, output: Path) -> FigureRecord:
    """Use signed cell values and separate scales for distinct endpoint units."""
    fig, _ = figure(6.54, 6.0)
    fig.clear()
    axes = panels(fig, vertical=True)
    precisions = sorted({r.recall_precision for r in audit.rows})
    concentrations = sorted({r.prior_concentration for r in audit.rows})
    for ax, endpoint, title in zip(
        axes,
        ("optimism", "brier"),
        (
            f"A  Optimism change contrast x {DISPLAY_SCALE:g}",
            f"B  Brier change contrast x {DISPLAY_SCALE:g}",
        ),
        strict=True,
    ):
        values: NDArray[np.float64] = np.array(
            [
                [
                    DISPLAY_SCALE
                    * next(
                        (
                            r.optimism_positive_minus_random
                            if endpoint == "optimism"
                            else r.brier_positive_minus_random
                        )
                        for r in audit.rows
                        if r.prior_concentration == c and r.recall_precision == p
                    )
                    for p in precisions
                ]
                for c in concentrations
            ]
        )
        limit = max(float(np.max(abs(values))), 1e-12)
        image = ax.imshow(values, cmap=DIVERGING_CMAP, vmin=-limit, vmax=limit, aspect="auto")
        for i in range(len(concentrations)):
            for j in range(len(precisions)):
                value = float(np.sum(values[i : i + 1, j : j + 1]))
                _ = ax.text(
                    j,
                    i,
                    f"{value:+.2f}",
                    ha="center",
                    va="center",
                    fontsize=11,
                    color="white" if abs(value) > 0.6 * limit else PALETTE["ink"],
                )
        _ = ax.set_xticks(range(len(precisions)), [f"{p:g}" for p in precisions])
        _ = ax.set_yticks(range(len(concentrations)), [f"{c:g}" for c in concentrations])
        _ = ax.set(xlabel="Recall likelihood precision", ylabel="Prior concentration", title=title)
        color_scale(fig, image, f"Signed contrast x {DISPLAY_SCALE:g}")
    return save(
        fig,
        output,
        "sensitivity",
        "GNN-admitted parameter sensitivity",
        "Positive-minus-random contrasts on a finite grid; separate zero-centered endpoint scales.",
        ("data/sensitivity.json",),
    )


def generate_figures(  # noqa: PLR0913, PLR0917 - Preserve the bundle-facing rendering API.
    study: StudyResult,
    report: StatisticalReport,
    absence: NothingnessAudit,
    attention: AttentionAudit,
    grid: SensitivityAudit,
    calibration: CalibrationAudit,
    output: Path,
) -> tuple[FigureRecord, ...]:
    """Render all eleven source-bound publication figures from admitted records."""
    return (
        concept_map(output),
        trajectories(study, output),
        calibration_by_world(study, report, output),
        paired_contrasts(report, output),
        paired_spread(report, output),
        weighting_sensitivity(report, output),
        appreciation_null(study, output),
        absence_information(absence, output),
        attention_policies(attention, output),
        sensitivity(grid, output),
        statistical_calibration(calibration, output),
    )
