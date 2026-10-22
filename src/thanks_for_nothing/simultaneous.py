# Copyright (c) 2026 Daniel Ari Friedman
"""Dependence-preserving, original-SE-standardized joint empirical-bootstrap regions."""

from dataclasses import replace
from math import ceil, sqrt
from typing import Final

import numpy as np
from numpy.typing import NDArray
from scipy.stats import binom

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.joint_contracts import (
    BLOCK_DIMENSIONS,
    MIN_PAIRED_UNITS,
    JointBlock,
    JointDesign,
    JointInterval,
    JointRegion,
)

FloatArray = NDArray[np.float64]
BOOTSTRAP_BATCH: Final = 128


def quantile_mc_bracket(
    roots: FloatArray, probability: float, confidence: float
) -> tuple[float | None, float | None]:
    """Conservative binomial order-statistic bounds, including ties and unbounded ranks.

    These bounds describe simulation error in a conditional bootstrap quantile.
    They are not a confidence interval for any scientific effect or its coverage.
    """
    if (
        roots.ndim != 1
        or not len(roots)
        or not np.isfinite(roots).all()
        or not 0 < probability < 1
        or not 0 < confidence < 1
    ):
        message = "Quantile bounds require finite roots and interior probabilities"
        raise ContractError(message)
    ordered = roots.copy()
    ordered.sort()
    tail = (1 - confidence) / 2
    lower = int(binom.ppf(tail, len(ordered), probability))
    upper = int(binom.ppf(1 - tail, len(ordered), probability)) + 1
    return (
        float(np.sum(ordered[lower - 1 : lower], dtype=np.float64)) if lower >= 1 else None,
        float(np.sum(ordered[upper - 1 : upper], dtype=np.float64)) if upper <= len(ordered) else None,
    )


def _admit(blocks: tuple[JointBlock, ...]) -> tuple[JointInterval, ...]:
    rows: list[JointInterval] = []
    keys: set[str] = set()
    names: set[str] = set()
    for block in blocks:
        values = block.values
        if (
            not block.name
            or block.name in names
            or values.ndim != BLOCK_DIMENSIONS
            or values.shape[0] < 1
            or values.shape[1] < MIN_PAIRED_UNITS
            or values.shape[2] < 1
            or len(block.keys) != values.shape[2]
            or len(block.exact_zero) != values.shape[2]
            or not np.isfinite(values).all()
        ):
            message = "Joint blocks require distinct names and finite stratum/unit/contrast arrays"
            raise ContractError(message)
        names.add(block.name)
        for index, (key, exact) in enumerate(zip(block.keys, block.exact_zero, strict=True)):
            if not key or key in keys:
                message = "Joint contrast identities must be nonempty and unique"
                raise ContractError(message)
            keys.add(key)
            strata, units = len(values), len(values.swapaxes(0, 1))
            column: FloatArray = values[:, :, index : index + 1].reshape(strata, units)
            if exact and (np.abs(column) > 0).any():
                message = "A mechanism-exact zero must be zero for every paired unit"
                raise ContractError(message)
            mean = float(np.mean(column))
            differences: FloatArray = column - column[:, :1]
            constant = not bool((np.abs(differences) > 0).any())
            variances = np.asarray(
                np.var(differences, axis=1, ddof=1, dtype=np.float64), dtype=np.float64
            )
            standard_error = (
                0.0 if constant else sqrt(float(np.sum(variances / units, dtype=np.float64))) / strata
            )
            if not np.isfinite((mean, standard_error)).all() or (standard_error == 0 and not constant):
                message = "Joint means and standard errors require numerically supported finite scale"
                raise ContractError(message)
            status = "mechanism_exact" if exact else "estimated"
            if standard_error == 0 and not exact:
                status = "unavailable_constant"
            rows.append(JointInterval(key, mean, standard_error, None, None, status))
    if not rows:
        message = "A joint family requires at least one contrast"
        raise ContractError(message)
    return tuple(rows)


def joint_region(blocks: tuple[JointBlock, ...], design: JointDesign) -> JointRegion:
    """Resample complete vectors within strata and independently across blocks.

    Every stochastic column is centered at its fitted mean and divided by its
    ORIGINAL standard error. This is a plug-in standardized maximum, explicitly
    different from resample-studentized bootstrap t. Coverage is asymptotic under
    joint bootstrap consistency, not a finite-sample or construct guarantee.
    """
    rows = _admit(blocks)
    stochastic = any(row.status == "estimated" for row in rows)
    roots = np.zeros(design.draws, dtype=np.float64)
    offset = 0
    for block_index, block in enumerate(blocks):
        block_rows = rows[offset : offset + len(block.keys)]
        offset += len(block.keys)
        keep = [index for index, row in enumerate(block_rows) if row.status == "estimated"]
        if not keep:
            continue
        values: FloatArray = block.values[:, :, keep]
        values = values - values[:, :1, :]
        strata, units = len(values), len(values.swapaxes(0, 1))
        means: FloatArray = np.asarray(np.mean(values, axis=(0, 1), dtype=np.float64), dtype=np.float64)
        errors = np.asarray([block_rows[index].standard_error for index in keep], dtype=np.float64)
        rng = np.random.default_rng(np.random.SeedSequence([design.seed, block_index]))
        for start in range(0, design.draws, BOOTSTRAP_BATCH):
            stop = min(start + BOOTSTRAP_BATCH, design.draws)
            indices = rng.integers(units, size=(stop - start, strata, units))
            sampled = np.take_along_axis(values[None, :, :, :], indices[:, :, :, None], axis=2)
            centered = np.mean(sampled, axis=(1, 2), dtype=np.float64) - means
            maxima = np.asarray(np.max(np.abs(centered / errors), axis=1), dtype=np.float64)
            roots[start:stop] = np.maximum(roots[start:stop], maxima)
    ordered = roots.copy()
    ordered.sort()
    rank = ceil(design.confidence * design.draws)
    critical = float(np.sum(ordered[rank - 1 : rank], dtype=np.float64)) if stochastic else None
    mc_low, mc_high = (
        quantile_mc_bracket(roots, design.confidence, design.monte_carlo_confidence)
        if stochastic
        else (None, None)
    )
    intervals: list[JointInterval] = []
    for row in rows:
        if row.status == "mechanism_exact":
            intervals.append(replace(row, low=0.0, high=0.0))
        elif row.status == "estimated" and critical is not None:
            margin = critical * row.standard_error
            intervals.append(replace(row, low=row.mean - margin, high=row.mean + margin))
        else:
            intervals.append(row)
    missing = any(row.status == "unavailable_constant" for row in intervals)
    status = "partial" if stochastic and missing else "complete"
    if not stochastic:
        status = "unavailable" if missing else "mechanism_exact"
    return JointRegion(
        design.confidence,
        design.draws if stochastic else 0,
        critical,
        mc_low,
        mc_high,
        design.monte_carlo_confidence,
        tuple((block.name, len(block.values), len(block.values.swapaxes(0, 1))) for block in blocks),
        tuple(intervals),
        status,
    )
