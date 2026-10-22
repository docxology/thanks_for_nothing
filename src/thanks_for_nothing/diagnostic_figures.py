# Copyright (c) 2026 Daniel Ari Friedman
"""Views separating paired-unit variation from sensitivity to world weights."""

from pathlib import Path

from thanks_for_nothing.contracts import Condition
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, panels, save
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE


def paired_spread(report: StatisticalReport, output: Path) -> FigureRecord:
    """Plot medians and unit IQRs, never labeling them confidence intervals."""
    fig, _ = figure(6.54, 6.0)
    fig.clear()
    axes = panels(fig, vertical=True)
    for ax, endpoint, title in zip(
        axes,
        ("brier_change", "nll_change"),
        ("A  Brier change: lower is better", "B  Log-loss change (nats): lower is better"),
        strict=True,
    ):
        for second, offset, marker in ((Condition.NO_RECALL, -0.02, "o"), (Condition.RANDOM, 0.02, "s")):
            rows = [
                r for r in report.heterogeneity.strata if r.endpoint == endpoint and r.second == second
            ]
            for index, row in enumerate(rows):
                y = row.world + offset
                _ = ax.plot(
                    [DISPLAY_SCALE * row.q25, DISPLAY_SCALE * row.q75], [y, y], color=PALETTE[second]
                )
                _ = ax.plot(
                    [DISPLAY_SCALE * row.median],
                    [y],
                    marker,
                    color=PALETTE[second],
                    label=f"Positive - {second.replace('_', ' ')}" if index == 0 else "_nolegend_",
                )
        worlds = sorted({r.world for r in report.heterogeneity.strata})
        _ = ax.axvline(0, color=PALETTE["ink"], lw=1)
        _ = ax.set_yticks(worlds, [f"{p:g}" for p in worlds])
        _ = ax.set(
            ylim=(min(worlds) - 0.08, max(worlds) + 0.08),
            xlabel=f"Positive minus comparator x {DISPLAY_SCALE:g}",
            ylabel="World P(well state)",
            title=title,
        )
        _ = ax.legend(loc="upper center")
    return save(
        fig,
        output,
        "paired_spread",
        "Between-unit variation within each world",
        "Dots are medians; segments span paired-unit quartiles, not confidence intervals.",
        ("data/statistics.json",),
    )


def weighting_sensitivity(report: StatisticalReport, output: Path) -> FigureRecord:
    """Show fixed-estimate weighting ranges without treating scenarios as samples."""
    fig, _ = figure(6.54, 5.5)
    fig.clear()
    axes = panels(fig, vertical=True)
    for ax, endpoint, title in zip(
        axes,
        ("brier_change", "nll_change"),
        ("A  Brier change: lower is better", "B  Log-loss change (nats): lower is better"),
        strict=True,
    ):
        rows = [r for r in report.heterogeneity.weighting if r.endpoint == endpoint]
        for index, row in enumerate(rows):
            _ = ax.plot(
                [DISPLAY_SCALE * row.convex_min, DISPLAY_SCALE * row.convex_max],
                [index, index],
                color=PALETTE["no_recall"],
                label="All world weights" if index == 0 else "_nolegend_",
            )
            if row.leave_one_out_min is not None and row.leave_one_out_max is not None:
                _ = ax.plot(
                    [DISPLAY_SCALE * row.leave_one_out_min, DISPLAY_SCALE * row.leave_one_out_max],
                    [index, index],
                    "s-",
                    color=PALETTE["matched_random_recall"],
                    label="Leave one world out" if index == 0 else "_nolegend_",
                )
            _ = ax.plot(
                [DISPLAY_SCALE * row.equal_grid.mean],
                [index],
                "D",
                color=PALETTE["ink"],
                label="Equal-grid mean" if index == 0 else "_nolegend_",
            )
        _ = ax.axvline(0, color=PALETTE["ink"], lw=1)
        _ = ax.set_yticks(range(len(rows)), ["Positive\n- No recall", "Positive\n- Random"])
        _ = ax.set(
            ylim=(-0.5, len(rows) - 0.5),
            title=title,
            xlabel=f"Positive minus comparator x {DISPLAY_SCALE:g}",
        )
        ax.invert_yaxis()
        _ = ax.legend(loc="upper center")
    return save(
        fig,
        output,
        "weighting_sensitivity",
        "Dependence on the world mixture",
        "Ranges vary world weights with estimated stratum means fixed; they are not CIs.",
        ("data/statistics.json",),
    )
