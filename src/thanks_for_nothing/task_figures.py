# Copyright (c) 2026 Daniel Ari Friedman
"""Task illustrations generated from admitted designs, without fabricated behavioral observations."""

from pathlib import Path

from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.concepts import MISSING_OBSERVATION, OBSERVED_ABSENCE
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, PlotAxes, figure, plot_grid, save


def _label(ax: PlotAxes, x: float, y: float, text: str, *, role: str = "ink") -> None:
    _ = ax.text(
        x, y, text, fontsize=10.5, va="center", ha="center", color=PALETTE[role], linespacing=1.4
    )


def _box(ax: PlotAxes, x: float, y: float, text: str, role: str = "no_recall") -> None:
    _ = ax.add_patch(
        FancyBboxPatch(
            (x - 0.14, y - 0.10),
            0.28,
            0.20,
            boxstyle="round,pad=0.015",
            facecolor="white",
            edgecolor=PALETTE[role],
            linewidth=1.5,
        )
    )
    _label(ax, x, y, text, role=role)


def _arrow(ax: PlotAxes, start: tuple[float, float], end: tuple[float, float]) -> None:
    _ = ax.add_patch(
        FancyArrowPatch(
            start, end, arrowstyle="->", mutation_scale=12, color=PALETTE["ink"], linewidth=1.3
        )
    )


def task_settings(bundle: ResearchBundle, output: Path) -> FigureRecord:
    """Show unknowns, evidence, choices and independent assessment for each foundational task."""
    fig, _ = figure(6.54, 6.2, automatic_layout=False)
    fig.clear()
    recall, absence, practice, scene = plot_grid(fig, (2, 2))
    for ax, title in zip(
        (recall, absence, practice, scene),
        (
            "(a) Paired recall",
            "(b) A / B: observation",
            "(c) D: enacted inquiry",
            "(d) Scene sampling",
        ),
        strict=True,
    ):
        _ = ax.set(xlim=(-0.04, 1.04), ylim=(0, 1), title=title)
        _ = ax.axis("off")
    study = bundle.study.design
    _label(recall, 0.5, 0.88, "World → observed events")
    for x, text, role in (
        (0.15, f"Train\n{study.baseline_days} days", "no_recall"),
        (0.5, f"Replay\n{study.intervention_days} days", "positive_recall"),
        (0.85, f"Test\n{study.evaluation_trials}", "no_recall"),
    ):
        _box(recall, x, 0.57, text, role)
    _arrow(recall, (0.31, 0.57), (0.34, 0.57))
    _arrow(recall, (0.66, 0.57), (0.69, 0.57))
    _label(recall, 0.5, 0.26, "Paired exposure; replay content differs.")
    _label(recall, 0.5, 0.10, "Assess on new observations;\nC adds value without belief learning.")
    _label(absence, 0.5, 0.88, "Hazard + recorder")
    for x, symbol, role in ((0.22, "∅", "positive_recall"), (0.78, "?", "no_recall")):
        _ = absence.add_patch(
            Circle((x, 0.59), 0.10, facecolor="white", edgecolor=PALETTE[role], linewidth=1.5)
        )
        _label(absence, x, 0.59, symbol, role=role)
    _label(absence, 0.22, 0.36, OBSERVED_ABSENCE.label.replace(" absence", "\nabsence"))
    _label(absence, 0.78, 0.36, MISSING_OBSERVATION.label.replace(" observation", "\nobservation"))
    _label(absence, 0.5, 0.10, "Only detected absence supplies\nevidence under the stated rule.")
    design = bundle.practice.design
    _label(practice, 0.5, 0.88, f"Choose activity; cost = {design.practice_cost:g}")
    _box(practice, 0.20, 0.58, "R family")
    _box(practice, 0.80, 0.58, "O family", "positive_recall")
    _arrow(practice, (0.37, 0.58), (0.62, 0.58))
    _label(
        practice,
        0.5,
        0.30,
        f"Calibrate {design.calibration_samples}; test {design.assessment_samples} new",
    )
    _label(practice, 0.5, 0.10, "Access may be blocked.\nEvidence selects retention or revision.")
    gaze = bundle.gaze.design
    _ = scene.add_patch(
        FancyBboxPatch(
            (0.03, 0.30),
            0.46,
            0.57,
            boxstyle="round,pad=0.015",
            facecolor="white",
            edgecolor=PALETTE["grid"],
        )
    )
    roles = ("positive_recall", "harm", "no_recall")
    markers = ("o", "v", "s")
    for (x, y), region in zip(gaze.coordinates, gaze.regions, strict=True):
        _ = scene.plot(
            [0.03 + 0.46 * x],
            [0.30 + 0.57 * y],
            markers[region],
            color=PALETTE[roles[region]],
            markersize=5,
        )
    _box(scene, 0.81, 0.73, "Agent\nq(m)")
    _arrow(scene, (0.64, 0.69), (0.51, 0.61))
    _label(scene, 0.81, 0.40, "Query\nObserve\nUpdate")
    _label(
        scene,
        0.5,
        0.10,
        f"{len(gaze.coordinates)} locations; {gaze.steps} decisions\nSchematic registered scene",
    )
    return save(
        fig,
        output,
        "task_settings",
        "What each foundational model does",
        "Paired recall, detected absence, missing records, costly inquiry and a schematic scene task.",
        (
            "data/concepts.json",
            "data/study.json",
            "data/nothingness.json",
            "data/emptiness_practice.json",
            "data/gaze.json",
        ),
    )


def boundary_task(bundle: ResearchBundle, output: Path) -> FigureRecord:
    """Make spatial evidence, nonspatial questions and the stipulated reference intervention visible."""
    fig, _ = figure(6.54, 6.0, automatic_layout=False)
    fig.clear()
    grid = GridSpec(2, 2, figure=fig, hspace=0.55)
    latent: PlotAxes = fig.add_subplot(grid[0, 0])
    probe: PlotAxes = fig.add_subplot(grid[0, 1])
    budget: PlotAxes = fig.add_subplot(grid[1, 0])
    target: PlotAxes = fig.add_subplot(grid[1, 1])
    for ax, title in zip(
        (latent, probe, budget, target),
        (
            "A  Scene and encoding",
            "B  Question the encoding",
            "C  One decision budget",
            "D  Separate assessments",
        ),
        strict=True,
    ):
        _ = ax.set(xlim=(-0.04, 1.04), ylim=(0, 1), title=title)
        _ = ax.axis("off")
    _box(latent, 0.20, 0.78, "Scene Z", "positive_recall")
    _box(latent, 0.80, 0.78, "Code H", "absence_appreciation")
    _arrow(latent, (0.24, 0.65), (0.43, 0.49))
    _arrow(latent, (0.76, 0.65), (0.57, 0.49))
    _box(latent, 0.5, 0.37, "W")
    _label(latent, 0.5, 0.10, "Spatial query → observation\nAppearance depends on Z and H.")
    reliability = bundle.boundary_gaze.design.probe_reliabilities
    middle = reliability[len(reliability) // 2]
    _box(probe, 0.20, 0.78, "Action a")
    _arrow(probe, (0.37, 0.78), (0.62, 0.78))
    _box(probe, 0.80, 0.78, "Result r", "absence_appreciation")
    for h in range(len(bundle.boundary_gaze.design.scene_maps)):
        _label(probe, 0.18 + h * 0.32, 0.46, f"H{h}\n0 → {h}", role="absence_appreciation")
    _label(probe, 0.5, 0.25, f"Modal r for a=0; reliability {middle:g}")
    _label(probe, 0.5, 0.08, "The pair informs H;\neach marginal alone is uniform.")
    design = bundle.boundary_gaze.design
    _ = budget.add_patch(
        Circle((0.5, 0.77), 0.10, facecolor="white", edgecolor=PALETTE["ink"], linewidth=1.5)
    )
    _label(budget, 0.5, 0.77, str(design.steps))
    _arrow(budget, (0.42, 0.64), (0.23, 0.48))
    _arrow(budget, (0.58, 0.64), (0.77, 0.48))
    _box(budget, 0.20, 0.34, f"{len(bundle.gaze.design.coordinates)} sites\nspatial", "positive_recall")
    _box(
        budget,
        0.80,
        0.34,
        f"{len(design.probe_reliabilities)} probes\nquestion",
        "absence_appreciation",
    )
    _label(budget, 0.5, 0.08, "Dependent decisions;\npaired potential outcomes.")
    _box(target, 0.5, 0.78, "q(Z,H)")
    _arrow(target, (0.45, 0.65), (0.24, 0.49))
    _arrow(target, (0.55, 0.65), (0.76, 0.49))
    _box(target, 0.20, 0.35, "Brier\nof H", "absence_appreciation")
    _box(target, 0.80, 0.35, f"Anchor\nH={design.anchor_mapping}", "positive_recall")
    _label(target, 0.5, 0.08, "Encoding and reference prediction:\nkeep current-scene risk and cost.")
    return save(
        fig,
        output,
        "boundary_task",
        "A task for gaze on an encoding",
        "Spatial and encoding queries share a budget; encoding and reference scores stay separate.",
        ("data/boundary_gaze.json", "data/gaze.json", "data/boundary_upstream.json"),
    )
