# Copyright (c) 2026 Daniel Ari Friedman
"""The pinned Gaussian comparator, separate from the scene-sampling cohort."""

from pathlib import Path

import numpy as np

from thanks_for_nothing.boundary_upstream import BoundaryUpstreamAudit
from thanks_for_nothing.visual_style import (
    DIVERGING_CMAP,
    PALETTE,
    FigureRecord,
    color_scale,
    figure,
    panels,
    save,
)


def boundary_structure(audit: BoundaryUpstreamAudit, output: Path) -> FigureRecord:
    """Keep Gaussian conditional structure separate from QRF label equality and the new cohort."""
    fig, _ = figure(6.54, 7.4)
    fig.clear()
    axes = panels(fig, vertical=True)
    for axis, values, title, limit in zip(
        axes,
        (audit.precision_matrix, audit.correlation_matrix),
        ("A  Known precision K", "B  Marginal correlation"),
        (max(abs(value) for row in audit.precision_matrix for value in row), 1.0),
        strict=True,
    ):
        matrix = np.asarray(values, dtype=np.float64)
        image = axis.imshow(matrix, cmap=DIVERGING_CMAP, vmin=-limit, vmax=limit)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                value = float(np.sum(matrix[i : i + 1, j : j + 1]))
                _ = axis.text(
                    j,
                    i,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    color=PALETTE["ink"] if abs(value) < limit / 2 else PALETTE["artwork_overlay"],
                )
        labels = [f"x{i}" for i in range(len(matrix))]
        _ = axis.set_xticks(list(range(len(matrix))), labels)
        _ = axis.set_yticks(list(range(len(matrix))), labels)
        _ = axis.set(title=title)
        color_scale(fig, image, "Precision coefficient" if axis is axes[0] else "Correlation")
    return save(
        fig,
        output,
        "boundary_structure",
        "A threshold limitation is not universal non-identifiability",
        (
            f"Pinned {len(audit.precision_matrix)}-variable Gaussian fixture; "
            "full covariance inversion recovers precision, "
            "while every marginal-correlation threshold misses the exact blanket."
        ),
        ("data/boundary_upstream.json",),
    )
