# Copyright (c) 2026 Daniel Ari Friedman
"""Exogenous attentional precision, with native GNN qualification kept distinct."""

from pathlib import Path
from tempfile import mkdtemp
from typing import TYPE_CHECKING, ClassVar, Final

import numpy as np
from gnn.execute.pymdp import run_pymdp_simulation
from gnn.render.pomdp_contract import build_canonical_pomdp_spec

if TYPE_CHECKING:
    from gnn.render.pomdp_contract import RuntimeParameters, TensorValues

from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing import contracts
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.inference import FloatArray, cumulative
from thanks_for_nothing.specifications import AdmittedModel, load_model
from thanks_for_nothing.standalone_gnn import ModelContext, standalone_model

NATIVE_TOLERANCE: Final = 1e-6

AttentionAudit = contracts.AttentionAudit
AttentionCondition = contracts.AttentionCondition
AttentionControls = contracts.AttentionControls
ReceiptRecord = contracts.ReceiptRecord

PROBABILITY_TOLERANCE: Final = 1e-8


class AttentionParameters(BaseModel):
    """All process and agent choices enter through GNN."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    num_timesteps: int = Field(ge=2, le=100)
    random_seed: int = Field(ge=0)
    policy_len: int = Field(ge=1, le=1)
    gamma: float = Field(gt=0)
    alpha: float = Field(gt=0)
    process_likelihood: tuple[tuple[float, ...], ...]
    positive_locations: tuple[int, ...]
    negative_locations: tuple[int, ...]
    neutral_locations: tuple[int, ...]


class NativeReceipt(BaseModel):
    """Consume numerical receipt fields; volatile runtime metadata is excluded."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    success: bool
    observations: tuple[int, ...]
    actions: tuple[int, ...]
    beliefs: tuple[tuple[float, ...], ...]
    policy_posterior: tuple[tuple[float, ...], ...]


def _valid(receipt: NativeReceipt, steps: int, states: int, actions: int, observations: int) -> bool:
    policies = np.asarray(receipt.policy_posterior, dtype=np.float64)
    beliefs = np.asarray(receipt.beliefs, dtype=np.float64)
    return bool(
        receipt.success
        and len(receipt.actions) == steps
        and len(receipt.observations) == steps
        and beliefs.shape == (steps, states)
        and policies.shape == (steps, actions)
        and np.isfinite(beliefs).all()
        and np.isfinite(policies).all()
        and (beliefs >= 0).all()
        and (policies >= 0).all()
        and np.max(np.abs(np.sum(beliefs, axis=1, dtype=np.float64) - 1)) < NATIVE_TOLERANCE
        and np.max(np.abs(np.sum(policies, axis=1, dtype=np.float64) - 1)) < NATIVE_TOLERANCE
        and all(0 <= a < actions for a in receipt.actions)
        and all(0 <= o < observations for o in receipt.observations)
    )


def _native(
    model: AdmittedModel,
    params: AttentionParameters,
    directory: Path,
    *,
    preferences: tuple[float, ...] | None = None,
    prior: tuple[float, ...] | None = None,
) -> NativeReceipt:
    tensors: TensorValues = {
        "A": model.tensors.A,
        "B": model.tensors.B,
        "C": model.tensors.C,
        "D": model.tensors.D,
    }
    if preferences is not None:
        tensors["C"] = preferences
    if prior is not None:
        tensors["D"] = prior
    knobs: RuntimeParameters = {
        "num_timesteps": params.num_timesteps,
        "random_seed": params.random_seed,
        "policy_len": params.policy_len,
        "gamma": params.gamma,
        "alpha": params.alpha,
        "b_tensor_order": "next_state_previous_state_action",
    }
    canonical = build_canonical_pomdp_spec(
        {"model_name": model.model_id, "initialparameterization": tensors, "model_parameters": knobs}
    )
    success, result = run_pymdp_simulation(canonical, directory)
    if not success:
        message = f"Native GNN execution failed: {result}"
        raise ContractError(message)
    return NativeReceipt.model_validate_json((directory / "simulation_results.json").read_text())


def _process(params: AttentionParameters, model: AdmittedModel | None = None) -> FloatArray:
    """Admit the common world channel before any native computation."""
    process = np.asarray(params.process_likelihood, dtype=np.float64)
    if model is None:
        model = load_model("attention_positive")
    expected = np.asarray(model.tensors.A).shape
    if (
        process.shape != expected
        or not np.isfinite(process).all()
        or (process < 0).any()
        or np.max(np.abs(np.sum(process, axis=0, dtype=np.float64) - 1)) >= PROBABILITY_TOLERANCE
    ):
        message = f"Attention process must be a normalized {expected} likelihood"
        raise ContractError(message)
    partition = params.positive_locations + params.negative_locations + params.neutral_locations
    if sorted(partition) != list(range(len(model.tensors.D))):
        message = "Attention locations must partition the declared states"
        raise ContractError(message)
    compiled = standalone_model(
        "attention_process",
        model.tensors.model_copy(update={"A": params.process_likelihood}),
        context=ModelContext(
            (model,),
            "thanks_for_nothing.attention:_fixed_process",
            "Fixed process A; agent A is separate. B,D retain location/action semantics.",
        ),
    )
    return np.asarray(compiled.tensors.A, dtype=np.float64)


def _fixed_process(model: AdmittedModel, params: AttentionParameters) -> AttentionCondition:
    import jax.numpy as jnp  # noqa: PLC0415 - Keep the optional native backend lazy.
    from pymdp.agent import Agent  # noqa: PLC0415 - Native attention boundary only.

    tensors = model.tensors
    process = _process(params, model)
    states = len(tensors.D)
    actions_count = len(tensors.B[0][0])
    agent = Agent(
        A=[jnp.asarray(tensors.A)[None]],
        B=[jnp.asarray(tensors.B)[None]],
        C=[jnp.asarray(tensors.C)[None]],
        D=[jnp.asarray(tensors.D)[None]],
        num_controls=[actions_count],
        control_fac_idx=[0],
        policy_len=params.policy_len,
        gamma=params.gamma,
        alpha=params.alpha,
        batch_size=1,
    )
    rng = np.random.default_rng(params.random_seed)
    prior = [jnp.asarray(tensors.D)[None]]
    state = int(np.sum(float(rng.random()) > cumulative(np.asarray(tensors.D, dtype=np.float64))))
    beliefs: list[tuple[float, ...]] = []
    policies: list[tuple[float, ...]] = []
    actions: list[int] = []
    observations: list[int] = []
    for _ in range(params.num_timesteps):
        observation = int(
            np.sum(
                float(rng.random()) > cumulative(process[:, state : state + 1].reshape(-1)),
                dtype=np.int64,
            )
        )
        qs, _ = agent.infer_states([jnp.array([observation])], empirical_prior=prior, return_info=True)
        q_pi, _ = agent.infer_policies(qs)
        policy: FloatArray = np.asarray(q_pi, dtype=np.float64).reshape(-1)
        action = int(np.sum(float(rng.random()) > cumulative(policy / np.sum(policy)), dtype=np.int64))
        prior = agent.update_empirical_prior(jnp.array([[action]]), qs)
        state = int(
            np.sum(
                float(rng.random())
                > cumulative(
                    np.asarray(tensors.B, dtype=np.float64)[
                        :, state : state + 1, action : action + 1
                    ].reshape(-1)
                ),
                dtype=np.int64,
            )
        )
        observations.append(observation)
        actions.append(action)
        belief_array: FloatArray = np.asarray(qs[0], dtype=np.float64)
        beliefs.append(tuple(float(np.sum(belief_array[:, -1:, i : i + 1])) for i in range(states)))
        policies.append(tuple(float(np.sum(policy[i : i + 1])) for i in range(actions_count)))
    masses = np.asarray(
        np.mean(np.asarray(policies, dtype=np.float64), axis=0, dtype=np.float64), dtype=np.float64
    )
    return AttentionCondition(
        model.model_id,
        float(np.sum(masses[list(params.positive_locations)])),
        float(np.sum(masses[list(params.negative_locations)])),
        float(np.sum(masses[list(params.neutral_locations)])),
        tuple(actions),
        tuple(observations),
        tuple(beliefs),
        tuple(policies),
        model.source_hash,
    )


def build_attention_audit(
    *, specification_dir: Path | None = None, output_dir: Path | None = None
) -> AttentionAudit:
    """Run bounded real native receipts plus fixed-process exogenous precision comparison."""
    directory = output_dir or Path(mkdtemp(prefix="tfn-attention-"))
    positive, negative = (
        load_model(name, specification_dir) for name in ("attention_positive", "attention_negative")
    )
    params = AttentionParameters.model_validate_json(positive.parameters_json)
    other = AttentionParameters.model_validate_json(negative.parameters_json)
    if params != other:
        message = "Attention comparison requires identical declared processes and runtime knobs"
        raise ContractError(message)
    if (
        np.asarray(positive.tensors.A).shape != np.asarray(negative.tensors.A).shape
        or np.asarray(positive.tensors.B).shape != np.asarray(negative.tensors.B).shape
    ):
        message = "Attention comparison requires identical tensor dimensions"
        raise ContractError(message)
    _ = _process(params, positive)
    first = _native(positive, params, directory / "positive")
    second = _native(negative, params, directory / "negative")
    c_probe = _native(
        positive,
        params,
        directory / "reverse-preferences",
        preferences=tuple(-v for v in positive.tensors.C),
    )
    d_probe = _native(
        positive,
        params,
        directory / "concentrated-prior",
        prior=(1.0,) + (0.0,) * (len(positive.tensors.D) - 1),
    )
    rows = (_fixed_process(positive, params), _fixed_process(negative, params))
    receipts = (first, second, c_probe, d_probe)
    controls: AttentionControls = {
        "native_receipts_valid": all(
            _valid(
                r,
                params.num_timesteps,
                len(positive.tensors.D),
                len(positive.tensors.B[0][0]),
                len(positive.tensors.A),
            )
            for r in receipts
        ),
        "fixed_process_valid": all(
            _valid(
                NativeReceipt(
                    success=True,
                    observations=r.observations,
                    actions=r.actions,
                    beliefs=r.beliefs,
                    policy_posterior=r.policy_posterior,
                ),
                params.num_timesteps,
                len(positive.tensors.D),
                len(positive.tensors.B[0][0]),
                len(positive.tensors.A),
            )
            for r in rows
        ),
        "c_changes_policy": bool(
            np.max(abs(np.asarray(first.policy_posterior) - np.asarray(c_probe.policy_posterior)))
            > PROBABILITY_TOLERANCE
        ),
        "d_changes_initial_belief": bool(
            np.max(abs(np.asarray(first.beliefs[0]) - np.asarray(d_probe.beliefs[0])))
            > PROBABILITY_TOLERANCE
        ),
        "exogenous_precision_changes_policy": bool(
            np.max(abs(np.asarray(rows[0].policy_posterior) - np.asarray(rows[1].policy_posterior)))
            > PROBABILITY_TOLERANCE
        ),
    }
    return AttentionAudit(
        rows,
        tuple(
            ReceiptRecord(r.success, r.observations, r.actions, r.beliefs, r.policy_posterior)
            for r in receipts
        ),
        controls,
        all(controls.values()),
        "Exogenous model probabilities; not empirical gaze/learned transfer. Native: matched-model A.",
    )
