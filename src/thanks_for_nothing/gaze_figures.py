# Copyright (c) 2026 Daniel Ari Friedman
"""Source reproduction and new learned/practice scanpaths on an attributed painting."""

from pathlib import Path

from thanks_for_nothing.gaze_art import ScenePath, artwork_credit, artwork_pixels, draw_scanpath
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, plot_grid, save


def yarbus_reconstruction(audit: GazeAudit, output: Path) -> FigureRecord:
    """Reproduce only the executable before-condition source results, including full-run counts."""
    fig, _ = figure(6.54, 7.0)
    fig.clear()
    first, second, positive, negative = plot_grid(fig, (2, 2))
    pixels = artwork_pixels(output)
    for axis, title, locations in (
        (first, "A  Source positive", audit.source.positive_states[0]),
        (second, "B  Source negative", audit.source.negative_states[0]),
    ):
        draw_scanpath(axis, audit.design, ScenePath(title, locations, pixels))
    for axis, title, percentages, role in (
        (positive, "C  Source positive", audit.source.positive_percent, "positive_recall"),
        (negative, "D  Source negative", audit.source.negative_percent, "harm"),
    ):
        _ = axis.bar([0, 1, 2], percentages, color=PALETTE[role])
        for index, value in enumerate(percentages):
            _ = axis.text(index, value + 2, f"{value:.2f}", ha="center", fontsize=10)
        _ = axis.set_xticks([0, 1, 2], ["Positive", "Negative", "Neutral"])
        _ = axis.set(ylim=(0, 100), ylabel="State occupancy (%)", title=title)
    artwork_credit(fig, "Rescaled background with model paths; no measured eye movements.")
    return save(
        fig,
        output,
        "yarbus_reconstruction",
        "Original gaze code reproduces the before condition",
        (
            f"Paths show {min(audit.design.trajectory_steps, len(audit.source.positive_states[0]))} "
            f"locations; occupancy pools {sum(map(len, audit.source.positive_states))} states/profile."
        ),
        ("data/gaze.json", "assets/scream-original.jpg", "assets/provenance.json"),
    )


def gaze_transfer_paths(audit: GazeAudit, output: Path) -> FigureRecord:
    """Show actual paired pre/post paths from the new belief-to-attention transfer mechanism."""
    fig, _ = figure(6.54, 7.6)
    fig.clear()
    axes = plot_grid(fig, (len(audit.design.example_strata), 2))
    pixels = artwork_pixels(output)
    for index, stratum in enumerate(audit.design.example_strata):
        row = next(
            row
            for row in audit.transfer
            if row.luckiness == stratum
            and row.replicate == 0
            and row.condition == "positive_recall"
            and row.bridge == "likelihood"
        )
        for phase, locations in enumerate((row.pre_locations, row.post_locations)):
            phase_name = "before" if phase == 0 else "after"
            title = f"{chr(65 + index * 2 + phase)}  p = {stratum:g}: {phase_name} recall"
            draw_scanpath(axes[index * 2 + phase], audit.design, ScenePath(title, locations, pixels))
    artwork_credit(fig, "Rescaled with model overlays; replicate zero is illustrative, not a mean.")
    return save(
        fig,
        output,
        "gaze_transfer_paths",
        "Learned recall transfer changes sampled locations",
        "Paired pre/post recall paths at actual luckiness strata, using the new declared transfer rule.",
        ("data/gaze.json", "data/study.json", "assets/scream-original.jpg", "assets/provenance.json"),
    )


def gaze_inquiry_paths(audit: GazeAudit, output: Path) -> FigureRecord:
    """Compare restricted utility sampling and open inquiry at equal observation budgets."""
    fig, _ = figure(6.54, 7.6)
    fig.clear()
    axes = plot_grid(fig, (len(audit.design.contexts), 2))
    pixels = artwork_pixels(output)
    for index, context in enumerate(audit.design.contexts):
        for column, condition in enumerate(("pragmatic_restricted", "inquiry_open")):
            row = next(
                row
                for row in audit.episodes
                if row.context == context.name
                and row.replicate == 0
                and row.window == audit.design.example_window
                and row.condition == condition
            )
            policy_name = "restricted" if column == 0 else "inquiry"
            title = f"{chr(65 + index * 2 + column)}  {context.name.capitalize()}: {policy_name}"
            draw_scanpath(
                axes[index * 2 + column], audit.design, ScenePath(title, row.locations, pixels)
            )
    artwork_credit(fig, "Fixed background; GNN context channels change, not image pixels.")
    return save(
        fig,
        output,
        "gaze_inquiry_paths",
        "Visual inquiry with restricted and revisable representations",
        "Sampled paths in stable and reversed channels; conditions share potential outcomes.",
        ("data/gaze.json", "assets/scream-original.jpg", "assets/provenance.json"),
    )
