# Copyright (c) 2026 Daniel Ari Friedman
"""Distinguish spatial scanpaths from nonspatial boundary questions in one paired example."""

from pathlib import Path

from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.gaze_art import ScenePath, artwork_credit, artwork_pixels, draw_scanpath
from thanks_for_nothing.gaze_contracts import GazeDesign
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, plot_grid, save


def boundary_paths(audit: BoundaryGazeAudit, gaze: GazeDesign, output: Path) -> FigureRecord:
    """Use replicate zero in the first scene at excluded H2; never select an example by its effect."""
    fig, _ = figure(6.54, 7.0)
    fig.clear()
    scene_axes = plot_grid(fig, (2, 2))
    pixels = artwork_pixels(output)
    excluded_boundary = len(audit.design.scene_maps) - 1
    location_count = len(gaze.coordinates)
    probe_count = len(audit.design.probe_costs)
    for index, condition in enumerate(("visual", "integrated")):
        row = next(
            r
            for r in audit.episodes
            if r.regime == "diagnostic"
            and r.boundary == excluded_boundary
            and r.scene == 0
            and r.replicate == 0
            and r.condition == condition
        )
        locations = tuple(q for q in row.queries if q < location_count)
        draw_scanpath(
            scene_axes[index],
            gaze,
            ScenePath(f"{'AB'[index]}  {condition.capitalize()}", locations, pixels),
        )
        timeline = [0 if query < location_count else query - location_count + 1 for query in row.queries]
        axis = scene_axes[index + 2]
        _ = axis.plot(
            list(range(1, len(timeline) + 1)),
            timeline,
            "o",
            color=PALETTE["positive_recall"] if index else PALETTE["no_recall"],
        )
        _ = axis.set_yticks(
            list(range(probe_count + 1)), ["Scene", *(f"Probe {i + 1}" for i in range(probe_count))]
        )
        _ = axis.set(
            xlabel="Decision index",
            ylim=(-0.5, probe_count + 0.5),
            title=f"{'CD'[index]}  Sampling schedule",
        )
    artwork_credit(fig, "Model scene samples above; nonspatial boundary questions below.")
    return save(
        fig,
        output,
        "boundary_gaze_paths",
        "Visual gaze and boundary inquiry share a finite budget",
        (
            f"First-scene replicate-zero example at H{excluded_boundary}; scene-only paths; "
            "timeline includes every decision."
        ),
        (
            "data/boundary_gaze.json",
            "data/gaze.json",
            "assets/scream-original.jpg",
            "assets/provenance.json",
        ),
    )
