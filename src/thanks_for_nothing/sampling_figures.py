# Copyright (c) 2026 Daniel Ari Friedman
"""Display paired effect stabilization and its conditional Monte Carlo standard error."""

from pathlib import Path

from matplotlib.ticker import NullFormatter

from thanks_for_nothing.sampling_diagnostics import SamplingAudit
from thanks_for_nothing.visual_style import PALETTE, FigureRecord, figure, plot_grid, save
from thanks_for_nothing.visual_tokens import PROCESS_ROLES


def sampling_precision(audit: SamplingAudit, output: Path) -> FigureRecord:
    """Use one-MCSE whiskers without implying confidence coverage or prefix independence."""
    fig, _ = figure(6.54, 6.6)
    fig.clear()
    axes = plot_grid(fig, (len(audit.cases), 2))
    for index, case in enumerate(audit.cases):
        left, right = axes[2 * index : 2 * index + 2]
        n = [p.replicates_per_stratum for p in case.points]
        means = [p.mean for p in case.points]
        errors = [p.monte_carlo_se for p in case.points]
        role = PROCESS_ROLES[index % len(PROCESS_ROLES)]
        _ = left.errorbar(
            n,
            means,
            yerr=[errors, errors],
            fmt="o-",
            capsize=2,
            color=PALETTE[role],
            label="Mean ± one MCSE",
        )
        _ = left.axhline(
            case.points[-1].mean, color=PALETTE["ink"], linestyle=":", lw=1, label="Full-budget mean"
        )
        _ = right.plot(n, errors, "s-", color=PALETTE[role], label="Paired-mean MCSE")
        _ = right.plot(
            n,
            [errors[-1] * (n[-1] / count) ** 0.5 for count in n],
            ":",
            color=PALETTE["ink"],
            label="Inverse-square-root guide",
        )
        _ = left.set(title=case.name, ylabel=case.units, xscale="log")
        _ = right.set(title="Sampling precision", ylabel=case.units, xscale="log", ylim=(0, None))
        ticks = sorted({*n[::2], n[-1]})
        stratum_label = "stratum" if case.points[-1].strata == 1 else "strata"
        for axis in (left, right):
            axis.xaxis.set_minor_formatter(NullFormatter())
            _ = axis.set_xticks(ticks, [str(count) for count in ticks])
            _ = axis.set(xlabel=f"Units / stratum ({case.points[-1].strata} {stratum_label})")
        _ = left.legend(loc="upper center")
        _ = right.legend(loc="upper center")
    return save(
        fig,
        output,
        "sampling_precision",
        "Independent sample size and Monte Carlo precision",
        "Nested paired-unit means and MCSE separate numerical precision from model uncertainty.",
        ("data/sampling_diagnostics.json", "data/analysis_protocol.json"),
    )
