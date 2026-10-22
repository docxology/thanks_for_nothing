# Copyright (c) 2026 Daniel Ari Friedman
"""Materialize, admit and record complete GNN models before numerical consumption."""

import json
import re
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from hashlib import sha256
from pathlib import Path
from typing import Final

import numpy as np
from gnn.utils.runtime_safety.safe_eval import MATRIX_MAX_LEN
from pydantic import JsonValue, TypeAdapter

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.specifications import AdmittedModel, Tensors, admit_model_source, load_model

_EVIDENCE: Final = {
    "recall_world": "study",
    "optimism_well": "study",
    "optimism_poor": "study",
    "attention_process": "attention",
    "practice_process": "emptiness_practice",
    "practice_restricted": "emptiness_practice",
    "scene_open": "gaze",
    "scene_restricted": "gaze",
    "transfer_embedding": "gaze",
    "boundary_diagnostic": "boundary_gaze",
    "boundary_label_only": "boundary_gaze",
    "boundary_diagnostic_restricted": "boundary_gaze",
    "boundary_label_only_restricted": "boundary_gaze",
}


@dataclass(frozen=True, slots=True)
class GenerativeModel:
    """One complete admitted model and its actual numerical consumer and origin bindings."""

    model_id: str
    family: str
    source_path: str
    source_sha256: str
    origins: tuple[tuple[str, str], ...]
    consumer: str
    meaning: str
    uses: int
    evidence_artifact: str = ""
    evidence_sha256: str = ""


@dataclass(frozen=True, slots=True)
class GenerativeCatalog:
    """Complete executed-family coverage tied to its numerical-run source identity."""

    schema: str
    source_tree_sha256: str
    models: tuple[GenerativeModel, ...]


@dataclass(slots=True)
class GenerativeRun:
    """A bounded execution scope retaining exactly the standalone models supplied to consumers."""

    output: Path
    models: dict[str, GenerativeModel] = field(default_factory=dict)

    def retain(
        self, source: str, record: GenerativeModel, origins: tuple[AdmittedModel, ...]
    ) -> AdmittedModel:
        """Read back the preserved GNN file before returning its tensors to the caller."""
        path = self.output / record.source_path
        for origin in origins:
            origin_path = (
                self.output / "specifications/origins" / f"{origin.model_id}_{origin.source_hash}.gnn.md"
            )
            origin_path.parent.mkdir(parents=True, exist_ok=True)
            if origin_path.exists() and origin_path.read_text() != origin.source_text:
                message = "Standalone GNN origin collision"
                raise ContractError(message)
            _ = origin_path.write_text(origin.source_text)
        previous = self.models.get(record.model_id)
        if previous is None:
            path.parent.mkdir(parents=True, exist_ok=True)
            _ = path.write_text(source)
            self.models[record.model_id] = record
        else:
            if previous.source_sha256 != record.source_sha256 or path.read_text() != source:
                message = "Standalone GNN identity collision or changed execution input"
                raise ContractError(message)
            self.models[record.model_id] = replace(
                previous,
                uses=previous.uses + 1,
                origins=tuple(sorted(set(previous.origins + record.origins))),
            )
        admitted = admit_model_source(path.read_text(), record.model_id)
        if admitted.source_hash != record.source_sha256:
            message = "Preserved standalone GNN differs from the consumed bytes"
            raise ContractError(message)
        return admitted

    def write(self) -> None:
        """Bind actual uses to the newly written numerical evidence, rejecting missing families."""
        if {m.family for m in self.models.values()} != _EVIDENCE.keys():
            message = "Incomplete standalone GNN generative-family coverage"
            raise ContractError(message)
        source = TypeAdapter(dict[str, JsonValue]).validate_json(
            (self.output / "data/source_tree.json").read_text()
        )
        catalog = GenerativeCatalog(
            "thanks_for_nothing.generative_models.v1",
            str(source["tree_sha256"]),
            tuple(
                replace(
                    model,
                    evidence_artifact=f"data/{_EVIDENCE[model.family]}.json",
                    evidence_sha256=file_digest(
                        self.output / "data" / f"{_EVIDENCE[model.family]}.json"
                    ),
                )
                for model in sorted(self.models.values(), key=lambda m: m.model_id)
            ),
        )
        write_record(self.output / "data/generative_models.json", catalog)


_ACTIVE: ContextVar[GenerativeRun | None] = ContextVar("standalone_gnn_run", default=None)


@contextmanager
def generative_run(output: Path) -> Generator[GenerativeRun]:
    """Scope instance custody to one real numerical run; nested scopes cannot silently replace it."""
    if _ACTIVE.get() is not None:
        message = "A standalone GNN execution scope is already active"
        raise ContractError(message)
    run = GenerativeRun(output)
    token = _ACTIVE.set(run)
    try:
        yield run
    finally:
        _ACTIVE.reset(token)


def _source(model_id: str, tensors: Tensors, parameters: dict[str, JsonValue], consumer: str) -> str:
    values = (("A", tensors.A), ("B", tensors.B), ("C", tensors.C), ("D", tensors.D))
    shapes = {name: np.asarray(value).shape for name, value in values}
    states, actions = len(tensors.D), len(tensors.B[0][0])
    variables = [
        *(f"{name}[{','.join(map(str, shape))},type=float]" for name, shape in shapes.items()),
        f"s[{states},type=float]",
        f"o[{len(tensors.C)},type=int]",
        f"u[{actions},type=int]",
    ]
    edges = ["D>s", "s>A", "A>o", "s>B", "u>B", "B>s", "C>u"]
    if parameters.get("query_count") is not None:
        variables.extend(
            (f"q[{parameters['query_count']},type=int]", f"z[{parameters['latent_count']},type=int]")
        )
        edges.extend(("q>s", "z>s", "u>q"))
    settings = [
        {
            "family": "standalone_generative",
            "backend": "pymdp",
            "consumer": consumer,
            "parameters": parameters,
            "claim_boundary": "Finite synthetic model; not empirical",
        }
    ]
    return (
        "\n\n".join(
            (
                "## GNNSection\nActInfPOMDP",
                "## GNNVersionAndFlags\nGNN v1",
                f"## ModelName\n{model_id}",
                f"## ModelAnnotation\n{parameters['meaning']}",
                "## StateSpaceBlock\n" + "\n".join(variables),
                "## Connections\n" + "\n".join(edges),
                "## InitialParameterization\n"
                + "\n".join(
                    [
                        *(name + "=" + _tensor_source(name, value) for name, value in values),
                        "settings=" + json.dumps(settings, separators=(",", ":")),
                    ]
                ),
            )
        )
        + "\n"
    )


def _tensor_source(name: str, value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"))
    if name in {"A", "B"}:
        if len(encoded) > MATRIX_MAX_LEN:
            message = "Standalone GNN tensor exceeds the upstream matrix safety envelope"
            raise ContractError(message)
        return "{" + encoded[1:-1].replace("[", "(").replace("]", ")") + "}"
    return encoded


@dataclass(frozen=True, slots=True)
class ModelContext:
    """Scientific origin and joint-state basis for an executable standalone declaration."""

    origins: tuple[AdmittedModel, ...]
    consumer: str
    meaning: str
    query_count: int | None = None
    latent_count: int | None = None
    initial_query: int = 0


def standalone_model(
    family: str,
    tensors: Tensors,
    *,
    context: ModelContext,
) -> AdmittedModel:
    """Compile a complete GNN source, admit its real bytes, then supply only admitted tensors."""
    if family not in _EVIDENCE:
        message = "Unknown standalone GNN scientific family"
        raise ContractError(message)
    parameters: dict[str, JsonValue] = {
        "family": family,
        "meaning": context.meaning,
        "provenance": "All originating GNN source versions are bound by data/generative_models.json",
    }
    if context.query_count is not None:
        parameters.update(
            query_count=context.query_count,
            latent_count=context.latent_count,
            initial_query=context.initial_query,
        )
    identity = sha256((_source(family, tensors, parameters, context.consumer)).encode()).hexdigest()
    model_id = f"{family}_{identity[:16]}"
    source = _source(model_id, tensors, parameters, context.consumer)
    record = GenerativeModel(
        model_id,
        family,
        f"specifications/instances/{model_id}.gnn.md",
        sha256(source.encode()).hexdigest(),
        tuple((m.model_id, m.source_hash) for m in context.origins),
        context.consumer,
        context.meaning,
        1,
    )
    run = _ACTIVE.get()
    return (
        admit_model_source(source, model_id)
        if run is None
        else run.retain(source, record, context.origins)
    )


def conditional_model(
    family: str,
    channels: FloatArray,
    prior: FloatArray,
    preferences: FloatArray,
    *,
    context: ModelContext,
) -> AdmittedModel:
    """Represent query-conditioned likelihoods as one explicit controlled joint-state POMDP."""
    queries, observations, latent = len(channels), len(preferences), len(prior)
    if channels.shape != (queries, observations, latent):
        message = "Query-conditioned GNN shape differs from its latent prior"
        raise ContractError(message)
    if not 0 <= context.initial_query < queries:
        message = "Initial GNN query lies outside its declared query basis"
        raise ContractError(message)
    state_count = queries * latent
    likelihood = channels.transpose(1, 0, 2).reshape(observations, state_count)
    transitions = np.zeros((state_count, state_count, queries), dtype=np.float64)
    for action in range(queries):
        for previous_query in range(queries):
            for state in range(latent):
                transitions[action * latent + state, previous_query * latent + state, action] = 1
    initial = np.zeros(state_count, dtype=np.float64)
    start = context.initial_query * latent
    initial[start : start + latent] = prior
    tensors = Tensors.model_validate({"A": likelihood, "B": transitions, "C": preferences, "D": initial})
    return standalone_model(
        family,
        tensors,
        context=replace(context, query_count=queries, latent_count=latent),
    )


def conditional_channels(model: AdmittedModel, queries: int) -> FloatArray:
    """Recover the numerical query channels exclusively from the admitted GNN likelihood."""
    likelihood = np.asarray(model.tensors.A, dtype=np.float64)
    return likelihood.reshape(len(model.tensors.C), queries, -1).transpose(1, 0, 2)


def read_generative_catalog(output: Path) -> GenerativeCatalog:
    """Reject omitted families, altered declarations and stale numerical evidence bindings."""
    catalog = TypeAdapter(GenerativeCatalog).validate_json(
        (output / "data/generative_models.json").read_text()
    )
    if (
        catalog.schema != "thanks_for_nothing.generative_models.v1"
        or {m.family for m in catalog.models} != _EVIDENCE.keys()
        or len({m.model_id for m in catalog.models}) != len(catalog.models)
        or catalog.source_tree_sha256
        != TypeAdapter(dict[str, JsonValue]).validate_json(
            (output / "data/source_tree.json").read_text()
        )["tree_sha256"]
    ):
        message = "Invalid standalone GNN coverage or numerical-run identity"
        raise ContractError(message)
    for entry in catalog.models:
        if entry.family not in _EVIDENCE or not re.fullmatch(r"[a-z_]+_[0-9a-f]{16}", entry.model_id):
            message = "Invalid standalone GNN model namespace"
            raise ContractError(message)
        path = output / "specifications/instances" / f"{entry.model_id}.gnn.md"
        model = load_model(entry.model_id, path.parent)
        content_identity = sha256(
            model.source_text.replace(
                f"## ModelName\n{entry.model_id}",
                f"## ModelName\n{entry.family}",
                1,
            ).encode()
        ).hexdigest()
        parameters = TypeAdapter(dict[str, JsonValue]).validate_json(model.parameters_json)
        if (
            entry.source_path != str(path.relative_to(output))
            or entry.model_id != f"{entry.family}_{content_identity[:16]}"
            or entry.source_sha256 != model.source_hash
            or entry.uses < 1
            or entry.evidence_artifact != f"data/{_EVIDENCE[entry.family]}.json"
            or entry.evidence_sha256 != file_digest(output / entry.evidence_artifact)
            or parameters["family"] != entry.family
            or parameters["meaning"] != entry.meaning
            or any(
                admit_model_source(
                    (output / "specifications/origins" / f"{name}_{digest}.gnn.md").read_text(),
                    name,
                ).source_hash
                != digest
                for name, digest in entry.origins
            )
        ):
            message = f"Standalone GNN model differs from consumed evidence: {entry.model_id}"
            raise ContractError(message)
    return catalog
