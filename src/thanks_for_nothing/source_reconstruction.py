# Copyright (c) 2026 Daniel Ari Friedman
"""Digest-bound numerical notebook reconstruction, deliberately retaining source behavior."""

from __future__ import annotations

import ast
import hashlib
import random
from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, ClassVar, Final

import numpy as np
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict, override

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.source_inputs import Array, Notebook, SourceInputError, source_bytes
from thanks_for_nothing.source_yarbus import (
    YARBUS_SHA256,
    YarbusAudit,
    YarbusReconstruction,
    build_yarbus_audit,
    run_yarbus_reconstruction,
)

if TYPE_CHECKING:
    from pathlib import Path

SOURCE_SHA256: Final = "1b8a0400ba6c457d1da8ca28a369f60be2f367fb760a794c78ce7125a321ceb6"
INTERVENTION_CELL: Final = 10
BEFORE_TASK_CELL: Final = 5
AFTER_TASK_CELL: Final = 12
NUMERICAL_CELLS: Final = (1, 5, 8, 10, 12, 14)


@dataclass(frozen=True, slots=True)
class SourceReconstruction:
    """Source arrays; baseline snapshots retain both pre/post alias mutation states."""

    seed: int
    luckiness: Array
    baseline: Array
    intervention: Array
    baseline_snapshots_before: Array
    baseline_snapshots_after: Array
    intervention_snapshots: Array
    updates_before: Array
    updates_after: Array
    task_priors_before: Array
    task_priors_after: Array
    average_day_before: Array
    average_day_after: Array
    shares_baseline_memory: bool


class SourceAudit(TypedDict):
    """Serializable measured notebook controls with bounded provenance."""

    source_sha256: str
    cell_count: int
    executed_cells: list[int]
    scope: str
    yarbus: YarbusAudit
    controls: dict[str, float | int | bool | list[float]]


class _Snapshots(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    A_matrices: Array
    A1: Array


class _TaskPriors(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    likelihood: tuple[float, ...]


class _SourceArrays(_Snapshots):
    luckiness: Array
    data: Array
    data_gratitude: Array
    A_matrices_gratitude: Array
    data_updates: Array
    data_updates_after: Array
    data_after_learning: Array
    data_averageday_gratitude: Array


def _cells(root: Path | None) -> list[str]:
    payload = source_bytes(root, "gratitude_original.ipynb")
    if hashlib.sha256(payload).hexdigest() != SOURCE_SHA256:
        msg = "Notebook does not match the independently pinned digest"
        raise SourceInputError(msg)
    return ["".join(cell.source) for cell in Notebook.model_validate_json(payload).cells]


class _Dimensions(ast.NodeTransformer):
    """Only substitute notebook dimension literals; source math remains unchanged."""

    def __init__(self, agents: int, days: int, steps: int) -> None:
        self.mapping: dict[int, int] = {1000: agents, 7: days, 12: steps, 6: days - 1, 11: steps - 1}

    @override
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if type(node.value) is int and node.value in self.mapping:
            return ast.copy_location(ast.Constant(self.mapping[node.value]), node)
        return node


def run_source_reconstruction(  # noqa: PLR0913 - preserve positional replay API with explicit protocol injection
    seed: int | None = None,
    agents: int | None = None,
    days: int | None = None,
    steps: int | None = None,
    *,
    root: Path | None = None,
    analysis: AnalysisDesign | None = None,
) -> SourceReconstruction:
    """Replay selected numeric cells, not Colab installation, plotting or stored outputs.

    Explicit dimensions are the caller-requested exploratory adapter, not upstream
    settings. RandomState retains the source NumPy sampling API; isolated seeded
    RNGs replace unseeded module globals. Cell 8 is included in correct source order.
    """
    protocol = load_analysis() if analysis is None else analysis
    seed = protocol.reconstruction_seed if seed is None else seed
    agents = protocol.reconstruction_agents if agents is None else agents
    days = protocol.reconstruction_days if days is None else days
    steps = protocol.reconstruction_steps if steps is None else steps
    for name, value, minimum in (
        ("seed", seed, 0),
        ("agents", agents, 1),
        ("days", days, 1),
        ("steps", steps, 1),
    ):
        if type(value) is not int or value < minimum:
            msg = f"{name} must be an integer >= {minimum}"
            raise SourceInputError(msg)
    if seed > 2**32 - 1:
        msg = "seed exceeds RandomState's uint32 range"
        raise SourceInputError(msg)
    cells = _cells(root)
    numpy_api = SimpleNamespace(
        **{
            name: getattr(np, name)
            for name in (
                "sum",
                "exp",
                "zeros",
                "linspace",
                "arange",
                "log",
                "inner",
                "outer",
                "dot",
                "mean",
                "where",
                "concatenate",
                "sort",
            )
        }
    )
    numpy_api.random = np.random.RandomState(seed)
    namespace = {"np": numpy_api, "random": random.Random(seed)}  # noqa: S311 - reproduces nonsecurity source sampling
    # Only the independently pinned softmax function is extracted from Colab setup.
    setup = ast.parse("\n".join(line for line in cells[0].splitlines() if not line.startswith("!")))
    softmax = next(
        node for node in setup.body if isinstance(node, ast.FunctionDef) and node.name == "softmax"
    )
    exec(compile(ast.Module(body=[softmax], type_ignores=[]), "source-cell-0", "exec"), namespace)  # noqa: S102 - independently digest-bound definition
    before = np.empty(0)
    priors_before = np.empty(0)
    priors_after = np.empty(0)
    shares_memory = False
    for index in NUMERICAL_CELLS:
        if index == INTERVENTION_CELL:
            before = _Snapshots.model_validate(namespace).A_matrices.copy()
        tree = ast.parse(cells[index])
        _ = _Dimensions(agents, days, steps).generic_visit(tree)
        tree = ast.fix_missing_locations(tree)
        exec(compile(tree, f"source-cell-{index}", "exec"), namespace)  # noqa: S102 - independently digest-bound cells
        if index == BEFORE_TASK_CELL:
            priors_before = np.array(_TaskPriors.model_validate(namespace).likelihood)
        if index == AFTER_TASK_CELL:
            priors_after = np.array(_TaskPriors.model_validate(namespace).likelihood)
        if index == INTERVENTION_CELL:
            snapshots = _Snapshots.model_validate(namespace)
            shares_memory = np.shares_memory(snapshots.A1, snapshots.A_matrices)
    arrays = _SourceArrays.model_validate(namespace)
    return SourceReconstruction(
        seed,
        arrays.luckiness,
        arrays.data,
        arrays.data_gratitude,
        before,
        arrays.A_matrices,
        arrays.A_matrices_gratitude,
        arrays.data_updates,
        arrays.data_updates_after,
        priors_before,
        priors_after,
        arrays.data_after_learning,
        arrays.data_averageday_gratitude,
        bool(shares_memory),
    )


def source_posterior(prior: Array, weights: Array) -> Array:
    """Source epsilon softmax algebra; zero weights allowed without taking log(0)."""
    if prior.shape != (2,) or weights.shape != (2,):
        msg = "prior and weights must each have shape (2,)"
        raise SourceInputError(msg)
    if not np.isfinite(prior).all() or not np.isfinite(weights).all():
        msg = "prior and weights must be finite"
        raise SourceInputError(msg)
    if (prior < 0).any() or (weights < 0).any() or abs(float(np.sum(prior)) - 1.0) > 1e-8 + 1e-5:
        msg = "prior must be a probability vector and weights nonnegative"
        raise SourceInputError(msg)
    product = prior * weights + 1e-5
    return product / np.sum(product)


def build_source_audit(root: Path, *, analysis: AnalysisDesign | None = None) -> SourceAudit:
    """Measure source-specific controls; no assertion about the paper's validity."""
    cells = _cells(root)
    protocol = load_analysis() if analysis is None else analysis
    run = run_source_reconstruction(
        agents=protocol.reconstruction_audit_agents, root=root, analysis=protocol
    )
    equal_prior = np.array([0.5, 0.5])
    counts = np.array([[9.0, 1.0], [9.0, 1.0], [0.0, 0.0]])
    raw = source_posterior(equal_prior, counts[:1].reshape(2))
    normalized = source_posterior(
        equal_prior, (counts / np.sum(counts, axis=0, dtype=np.float64))[:1].reshape(2)
    )
    # Equivalent categorical endpoint control for source belief [well=1, poor=0].
    selected = int(np.random.RandomState(1).multinomial(1, [1.0, 0.0]).argmax())
    bins = np.arange(0.1, 1.0, 0.1)
    grid = np.linspace(0.1, 0.9, 1000)
    return {
        "yarbus": build_yarbus_audit(root),
        "source_sha256": SOURCE_SHA256,
        "cell_count": len(cells),
        "executed_cells": [0, *NUMERICAL_CELLS],
        "scope": (
            "Digest-bound selected numeric cells; seeded headless dimension adapter; "
            "not full Colab replication"
        ),
        "controls": {
            "belief_well_one_selects_index": selected,
            "optimistic_comment_index": 1,
            "label_reversal_observed": selected != 1,
            "raw_counts_posterior_well": float(np.sum(raw[:1])),
            "normalized_posterior_well": float(np.sum(normalized[:1])),
            "counts_mass_effect": float(np.sum((raw - normalized)[:1])),
            "source_epsilon_zero_weight_leak": float(
                np.sum(source_posterior(equal_prior, np.array([1.0, 0.0]))[1:])
            ),
            "snapshots_share_memory": run.shares_baseline_memory,
            "snapshot_mutation_max": float(
                np.max(abs(run.baseline_snapshots_before - run.baseline_snapshots_after))
            ),
            "baseline_snapshot_initial_total": float(np.sum(run.baseline_snapshots_before[:1, :1])),
            "baseline_snapshot_last_total": float(np.sum(run.baseline_snapshots_before[:1, -1:])),
            "task_priors_redrawn": bool((abs(run.task_priors_before - run.task_priors_after) > 0).any()),
            "intervention_exact_one_count": int(
                np.sum(abs(run.intervention[:, :, 2:3] - 1) <= 0, dtype=np.int64)
            ),
            "plot_first_five_actual_luckiness": grid[:5].tolist(),
            "plot_excluded_grid_points": int(
                np.sum(np.digitize(grid, bins) >= len(bins), dtype=np.int64)
            ),
            "normal_numeric_order_completes": bool(np.isfinite(run.intervention).all()),
        },
    }


__all__ = [
    "SOURCE_SHA256",
    "YARBUS_SHA256",
    "SourceAudit",
    "SourceInputError",
    "SourceReconstruction",
    "YarbusAudit",
    "YarbusReconstruction",
    "build_source_audit",
    "build_yarbus_audit",
    "run_source_reconstruction",
    "run_yarbus_reconstruction",
    "source_posterior",
]
