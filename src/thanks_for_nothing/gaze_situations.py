# Copyright (c) 2026 Daniel Ari Friedman
"""Scene sampling and inquiry into its encoding, beside their finite-model consequences."""

from pathlib import Path
from textwrap import fill

from matplotlib.ticker import MaxNLocator

from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.figure_keys import interval_marker
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_joint import GazeUncertainty
from thanks_for_nothing.situation_drawing import (
    SituationLink,
    SituationNode,
    diagram_note,
    draw_link,
    draw_node,
    situation_canvas,
)
from thanks_for_nothing.visual_style import LABELS, PALETTE, FigureRecord, save
from thanks_for_nothing.visual_tokens import BOUNDARY_LABELS, BOUNDARY_ROLES, GAZE_LABELS


def gaze_situation(audit: GazeAudit, uncertainty: GazeUncertainty, output: Path) -> FigureRecord:
    """Make the scene, belief, sampling loop, and two separate result questions explicit."""
    fig, setting, attention, comparison = situation_canvas(
        "Look, observe, update, and choose a site",
        "Tests: learned transfer; inquiry against already-open comparators",
        stacked=True,
    )
    roles, markers = ("positive_recall", "harm", "no_recall"), ("o", "v", "s")
    for region, (role, marker) in enumerate(zip(roles, markers, strict=True)):
        sites = [
            point
            for point, group in zip(audit.design.coordinates, audit.design.regions, strict=True)
            if group == region
        ]
        _ = setting.plot(
            [0.02 + 0.36 * point[0] for point in sites],
            [0.20 + 0.65 * point[1] for point in sites],
            marker,
            color=PALETTE[role],
            markersize=6,
        )
    diagram_note(setting, (0.21, 0.99), f"Scene: {len(audit.design.coordinates)} sites")
    for node in (
        SituationNode((0.65, 0.97), "Learned\nA / readout"),
        SituationNode((0.65, 0.59), "Belief q\nscene/model", "positive_recall", "belief"),
        SituationNode((0.90, 0.28), "Policy\nnext site", "matched_random_recall"),
    ):
        draw_node(setting, node)
    for link in (
        SituationLink((0.40, 0.59), (0.53, 0.59)),
        SituationLink((0.65, 0.84), (0.65, 0.73)),
        SituationLink((0.76, 0.56), (0.88, 0.41)),
        SituationLink((0.79, 0.28), (0.40, 0.28)),
        SituationLink((0.77, 0.96), (0.91, 0.41), dashed=True),
    ):
        draw_link(setting, link)
    diagram_note(setting, (0.45, 0.74), "Observe")
    diagram_note(setting, (0.59, 0.16), "Query chosen site")
    diagram_note(
        setting,
        (0.50, -0.01),
        f"{audit.design.steps} decisions / active episode; observations use synthetic likelihoods",
    )
    rows = [
        r
        for r in audit.contrasts
        if r.experiment == "transfer"
        and r.context == "likelihood"
        and r.endpoint == "positive_policy_change"
        and r.reference == "no_recall"
    ]
    _ = attention.axvline(0, color=PALETTE["ink"], lw=1)
    for index, row in enumerate(rows):
        interval = row.intervals
        _ = attention.errorbar(
            [100 * interval.mean],
            [index],
            xerr=[
                [100 * (interval.mean - interval.analytic_low)],
                [100 * (interval.analytic_high - interval.mean)],
            ],
            fmt="o",
            capsize=3,
            color=PALETTE[row.condition],
            label=f"b: {LABELS[row.condition]}",
        )
    _ = attention.set_yticks(list(range(len(rows))), [fill(LABELS[r.condition], 17) for r in rows])
    _ = attention.set(
        title="b  Learned likelihood bridge",
        xlabel="Positive-site policy change\nminus no recall (pp)",
        ylim=(len(rows) - 0.4, -0.6),
    )
    joint = {r.key: r for r in uncertainty.region.intervals}
    active = [
        r
        for r in audit.contrasts
        if r.experiment == "active"
        and r.endpoint == "mean_balanced_log_loss"
        and r.condition == "inquiry_open"
        and r.reference in ("pragmatic_open", "uniform_open")
    ]
    _ = comparison.axvline(0, color=PALETTE["ink"], lw=1)
    labels: list[str] = []
    for index, row in enumerate(active):
        reference = GAZE_LABELS[row.reference].lower()
        labels.append(f"{row.context.capitalize()}:\nvs {reference}")
        point = row.intervals
        region = joint[f"active/{row.context}/{row.condition}/{row.reference}/{row.endpoint}"]
        _ = comparison.errorbar(
            [point.mean],
            [index - 0.10],
            xerr=[[point.mean - point.analytic_low], [point.analytic_high - point.mean]],
            fmt="o",
            capsize=2,
            color=PALETTE["no_recall"],
            label="c: Pointwise analytic interval" if index == 0 else "_nolegend_",
        )
        if region.low is not None and region.high is not None:
            _ = comparison.errorbar(
                [region.mean],
                [index + 0.10],
                xerr=[[region.mean - region.low], [region.high - region.mean]],
                fmt="D",
                capsize=3,
                color=PALETTE["positive_recall"],
                label="c: Joint bootstrap bounds" if index == 0 else "_nolegend_",
            )
        else:
            _ = comparison.plot(
                [region.mean],
                [index + 0.10],
                "x",
                color=PALETTE["harm"],
                label="c: Interval unavailable",
            )
    _ = comparison.set_yticks(list(range(len(active))), labels)
    _ = comparison.set(
        title="c  Inquiry vs open sampling",
        xlabel="Scene loss difference\n(nats / outcome)",
        ylim=(len(active) - 0.4, -0.6),
    )
    comparison.xaxis.set_major_locator(MaxNLocator(nbins=3))
    return save(
        fig,
        output,
        "gaze_situation",
        "A scene-sampling task with distinct attention and prediction targets",
        "Scene sites, belief, sampling, attention transfer and inquiry with distinct bounds.",
        ("data/gaze.json", "data/gaze_uncertainty.json", "data/study.json"),
    )


def boundary_situation(audit: BoundaryGazeAudit, output: Path) -> FigureRecord:
    """Show what scene queries and action-response questions reveal to the same joint belief."""
    design = audit.design
    fig, setting, risk, encoding = situation_canvas(
        "Ask about the scene and its encoding",
        "Test: do scene samples and encoding questions support reference transfer?",
    )
    for node in (
        SituationNode((0.09, 0.85), "Scene\nZ", "positive_recall", "world"),
        SituationNode((0.09, 0.31), "Code\nH", "absence_appreciation", "world"),
        SituationNode((0.35, 0.85), "Spatial\nobservation", "positive_recall"),
        SituationNode((0.35, 0.31), "Question\na, response r", "absence_appreciation"),
        SituationNode((0.63, 0.59), "Joint belief\nq(Z,H)", "ink", "belief"),
        SituationNode((0.90, 0.85), f"Predict at\nH={design.anchor_mapping}", "positive_recall"),
        SituationNode((0.90, 0.31), "Encoding\nBrier loss", "absence_appreciation"),
    ):
        draw_node(setting, node)
    for start, end in (
        ((0.18, 0.85), (0.24, 0.85)),
        ((0.18, 0.31), (0.24, 0.31)),
        ((0.16, 0.43), (0.27, 0.73)),
        ((0.45, 0.85), (0.52, 0.67)),
        ((0.45, 0.31), (0.52, 0.51)),
        ((0.75, 0.67), (0.79, 0.85)),
        ((0.75, 0.51), (0.79, 0.31)),
    ):
        draw_link(setting, SituationLink(start, end))
    diagram_note(
        setting,
        (0.50, -0.01),
        f"One {design.steps}-decision budget; {design.replicates} paired units / fixed scene stratum",
    )
    excluded = len(design.scene_maps) - 1
    conditions = tuple(c for c in design.conditions if c != "visual")
    indexed = {r.key: r for r in audit.region.intervals}
    for axis, endpoint, title, units in (
        (
            risk,
            "anchored_regret",
            f"b  H{excluded}: reference prediction",
            "Nats / outcome minus visual only",
        ),
        (
            encoding,
            "boundary_brier",
            f"c  H{excluded}: encoding estimate",
            "Brier loss minus visual only",
        ),
    ):
        _ = axis.axvline(0, color=PALETTE["ink"], lw=1)
        for index, condition in enumerate(conditions):
            row = indexed[f"diagnostic/H{excluded}/{condition}/visual/{endpoint}"]
            color = PALETTE[BOUNDARY_ROLES[condition]]
            if row.low is None or row.high is None:
                _ = axis.plot([row.mean], [index], "x", color=color)
            else:
                marker = interval_marker(row.status)
                _ = axis.errorbar(
                    [row.mean],
                    [index],
                    xerr=[[row.mean - row.low], [row.high - row.mean]],
                    fmt=marker,
                    capsize=3,
                    color=color,
                )
        _ = axis.set_yticks(
            list(range(len(conditions))), [fill(BOUNDARY_LABELS[c], 12) for c in conditions]
        )
        _ = axis.set(title=title, xlabel=fill(units, 25), ylim=(len(conditions) - 0.4, -0.6))
        axis.xaxis.set_major_locator(MaxNLocator(nbins=3))
    return save(
        fig,
        output,
        "boundary_situation",
        "Encoding information needs scene evidence for reference prediction",
        "Scene and encoding queries feed distinct risk and Brier targets; exact values stay marked.",
        ("data/boundary_gaze.json", "data/gaze.json"),
    )
