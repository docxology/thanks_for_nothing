# Copyright (c) 2026 Daniel Ari Friedman
"""Pointwise inference from the same paired vectors used by joint uncertainty."""

import numpy as np

from thanks_for_nothing.gaze_contracts import GazeContrast, GazeEpisode, TransferGaze
from thanks_for_nothing.gaze_design import GazeTask
from thanks_for_nothing.gaze_samples import active_samples, transfer_samples
from thanks_for_nothing.intervals import mean_intervals


def transfer_contrasts(rows: tuple[TransferGaze, ...], task: GazeTask) -> tuple[GazeContrast, ...]:
    """Preserve the pointwise draw order over whole agents within fixed strata."""
    rng = np.random.default_rng(np.random.SeedSequence([task.design.seed, 1]))
    return tuple(
        GazeContrast(
            *sample.identity,
            mean_intervals(
                sample.values, task.design.bootstrap_draws, rng, confidence=1 - task.analysis.alpha
            ),
            len(sample.values) * len(sample.values.T),
        )
        for sample in transfer_samples(rows, task.design)
    )


def active_contrasts(rows: tuple[GazeEpisode, ...], task: GazeTask) -> tuple[GazeContrast, ...]:
    """Preserve pointwise draws after within-replicate window aggregation."""
    rng = np.random.default_rng(np.random.SeedSequence([task.design.seed, 2]))
    return tuple(
        GazeContrast(
            *sample.identity,
            mean_intervals(
                sample.values, task.design.bootstrap_draws, rng, confidence=1 - task.analysis.alpha
            ),
            task.design.replicates,
        )
        for sample in active_samples(rows, task.design)
    )
