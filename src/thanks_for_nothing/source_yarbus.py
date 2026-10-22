# Copyright (c) 2026 Daniel Ari Friedman
"""Digest-bound execution and numerical controls for the recovered Yarbus class."""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from types import SimpleNamespace
from typing import TYPE_CHECKING, ClassVar, Final, Protocol, runtime_checkable

import numpy as np
from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

from thanks_for_nothing.gaze_contracts import GazeDesign, SourceGaze
from thanks_for_nothing.source_inputs import Array, Notebook, SourceInputError, source_bytes

if TYPE_CHECKING:
    from pathlib import Path

    from numpy.typing import NDArray

YARBUS_SHA256: Final = "ab9f36b515d1534d24b7e676841fa5cea7c264370f6ee566798c8b1b3de62510"
SOURCE_POSITIVE_BOUND: Final = 5
SOURCE_AFFECTIVE_BOUND: Final = 10
YARBUS_RECONSTRUCTION_SEED: Final = 42
YARBUS_RECONSTRUCTION_STEPS: Final = 100


@dataclass(frozen=True, slots=True)
class YarbusReconstruction:
    """Captured original class arrays in its actual action-first transition convention."""

    states: NDArray[np.int64]
    observations: Array
    priors: Array
    policies: Array
    likelihood: Array
    process: Array
    transitions: Array
    initial_efe: Array


class _YarbusAgent(Protocol):
    x1: NDArray[np.int64]
    O: Array  # noqa: E741 - retained original source class attribute
    X1: Array
    Pi: Array
    A1: Array
    a1: Array
    B1: Array

    def compute_expected_free_energy(self, t: int) -> Array: ...
    def run_simulation(self) -> tuple[Array, Array, NDArray[np.int64]]: ...


@runtime_checkable
class _YarbusFactory(Protocol):
    def __call__(self, *, time_steps: int, agent_type: str) -> _YarbusAgent: ...


class _YarbusNamespace(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    YarbusActiveInference: _YarbusFactory


def _yarbus_namespace(root: Path | None, seed: int) -> _YarbusNamespace:
    """Admit immutable source and extract numerical definitions, excluding entrypoints."""
    payload = source_bytes(root, "yarbus_original.ipynb")
    if hashlib.sha256(payload).hexdigest() != YARBUS_SHA256:
        msg = "Yarbus notebook does not match the independently pinned digest"
        raise SourceInputError(msg)
    tree = ast.parse("".join(Notebook.model_validate_json(payload).cells[1].source))
    definitions: list[ast.stmt] = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "YarbusActiveInference"
    ]
    numpy_api = SimpleNamespace(
        **{name: getattr(np, name) for name in ("zeros", "array", "sum", "log", "max", "exp", "dot")}
    )
    numpy_api.random = np.random.RandomState(seed)
    namespace = {"np": numpy_api}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), "yarbus-cell-1", "exec"), namespace)  # noqa: S102 - independently digest-bound class
    return _YarbusNamespace.model_validate(namespace)


def run_yarbus_reconstruction(
    seed: int = YARBUS_RECONSTRUCTION_SEED,
    steps: int = YARBUS_RECONSTRUCTION_STEPS,
    agent_type: str = "positive",
    *,
    root: Path | None = None,
) -> YarbusReconstruction:
    """Run the digest-bound source class with isolated RNG and fixed source 13 states."""
    if type(seed) is not int or not 0 <= seed <= 2**32 - 1:
        msg = "seed must be a uint32 integer"
        raise SourceInputError(msg)
    if type(steps) is not int or steps < 1:
        msg = "steps must be a positive integer"
        raise SourceInputError(msg)
    if agent_type not in ("positive", "negative"):
        msg = "agent_type must be positive or negative"
        raise SourceInputError(msg)
    location = root
    namespace = _yarbus_namespace(location, seed)
    agent = namespace.YarbusActiveInference(time_steps=steps, agent_type=agent_type)
    # A distinct source instance measures EFE without consuming the trajectory RNG.
    probe_namespace = _yarbus_namespace(location, seed)
    probe = probe_namespace.YarbusActiveInference(time_steps=1, agent_type=agent_type)
    efe = probe.compute_expected_free_energy(0)
    _ = agent.run_simulation()
    return YarbusReconstruction(agent.x1, agent.O, agent.X1, agent.Pi, agent.A1, agent.a1, agent.B1, efe)


def run_yarbus_cohort(design: GazeDesign, root: Path | None = None) -> SourceGaze:
    """Preserve the original entrypoint's shared seed, alternating order and five full runs."""
    namespace = _yarbus_namespace(root, design.source_seed)
    positive: list[tuple[int, ...]] = []
    negative: list[tuple[int, ...]] = []
    for _ in range(design.source_runs):
        for label, storage in (("positive", positive), ("negative", negative)):
            agent = namespace.YarbusActiveInference(time_steps=design.source_steps, agent_type=label)
            _ = agent.run_simulation()
            storage.append(tuple(int(np.sum(agent.x1[i : i + 1])) for i in range(len(agent.x1))))
    percentages: list[tuple[float, ...]] = []
    for runs in (positive, negative):
        states = np.asarray(runs, dtype=np.int64)
        percentages.append(
            tuple(
                100 * float(np.mean(mask))
                for mask in (
                    states < SOURCE_POSITIVE_BOUND,
                    (states >= SOURCE_POSITIVE_BOUND) & (states < SOURCE_AFFECTIVE_BOUND),
                    states >= SOURCE_AFFECTIVE_BOUND,
                )
            )
        )
    published = ((82.1, 11.0, 6.9), (54.6, 11.8, 33.6))
    return SourceGaze(
        YARBUS_SHA256,
        tuple(positive),
        tuple(negative),
        percentages[0],
        percentages[1],
        tuple(tuple(round(value, 1) for value in row) for row in percentages) == published,
        after_intervention_available=False,
    )


class YarbusAudit(TypedDict):
    """Serializable source-class controls and source identity."""

    source_sha256: str
    executed_definition: str
    controls: dict[str, float | int | bool]


def build_yarbus_audit(root: Path) -> YarbusAudit:
    """Numerical counterexamples and null controls under the source's actual axes."""
    run = run_yarbus_reconstruction(root=root)
    entropy = -np.sum(run.likelihood * np.log(run.likelihood + 1e-10), axis=0, dtype=np.float64)
    oracle = -run.likelihood.T @ np.array([2.0, 0.0, -2.0]) + 0.5 * entropy
    oracle += np.random.RandomState(YARBUS_RECONSTRUCTION_SEED).normal(0, 0.1, 13)
    expected = np.zeros((13, 13, 13))
    for action in range(13):
        expected[action, action, :] = 1
    next_states = run.priors[:, 1:].argmax(axis=0, out=np.empty(len(run.states) - 1, dtype=np.int64))
    return {
        "source_sha256": YARBUS_SHA256,
        "executed_definition": "cell 1: YarbusActiveInference only",
        "controls": {
            "action_first_transition_matches_target": bool((abs(run.transitions - expected) <= 0).all()),
            "transition_prior_min_mass": float(np.min(np.sum(run.priors, axis=0, dtype=np.float64))),
            "transition_prior_max_mass": float(np.max(np.sum(run.priors, axis=0, dtype=np.float64))),
            "prior_argmax_matches_actual_next_state": bool(
                (abs(next_states - run.states[1:]) <= 0).all()
            ),
            "observation_process_mismatch_count": int(
                np.sum(
                    np.take_along_axis(
                        run.process.take(run.states, axis=1),
                        run.observations.astype(np.int64).reshape(1, -1),
                        axis=0,
                    )
                    <= 0,
                    dtype=np.int64,
                )
            ),
            "likelihood_process_max_difference": float(np.max(abs(run.likelihood - run.process))),
            "efe_ambiguity_cost_oracle_max_error": float(np.max(abs(run.initial_efe - oracle))),
            "uncomputed_final_policy_mass": float(np.sum(run.policies[:, -1:])),
        },
    }
