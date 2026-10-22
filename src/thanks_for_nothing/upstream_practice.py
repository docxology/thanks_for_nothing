# Copyright (c) 2026 Daniel Ari Friedman
"""Admit the real upstream practice vocabulary and bounded ongoing-revision diagnostic."""

import inspect
import json
from dataclasses import dataclass
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from typing import ClassVar, Literal

from practice.protocols import practice_protocol_map
from pydantic import BaseModel, ConfigDict
from simulation.emergence import build_ongoing_revision_audit

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.provenance import file_digest


class _Protocol(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    id: str
    paper_role: str
    model_intervention: dict[str, float]
    safety_boundary: str


class _Protocols(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    allow_user_facing_claims: Literal[False]
    protocol_count: int
    protocols: tuple[_Protocol, ...]
    all_have_safety_boundaries: Literal[True]


class _Revision(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    label: str
    controls: dict[str, bool]
    all_controls_pass: bool
    claim_boundary: str


@dataclass(frozen=True, slots=True)
class UpstreamPracticeAudit:
    """Metadata is not an enacted protocol; upstream revision uses in-sample window scores."""

    schema: str
    protocol_ids: tuple[str, ...]
    protocol_map_sha256: str
    upstream_revision_sha256: str
    module_sha256: dict[str, str]
    revision_controls: dict[str, bool]
    all_controls_pass: bool
    practice_deltas_enacted_upstream: bool = False
    revision_assessment_held_out: bool = False


def build_upstream_practice_audit() -> UpstreamPracticeAudit:
    """Call installed upstream APIs and bind their actual module bytes and serialized receipts."""
    raw_protocols = practice_protocol_map()
    protocols = _Protocols.model_validate(raw_protocols)
    raw_revision = build_ongoing_revision_audit()
    revision = _Revision.model_validate(raw_revision)
    identities = {row.id for row in protocols.protocols}
    if (
        identities
        != {"attentional_opacification", "dependent_origination_inquiry", "compassion_alignment"}
        or len(protocols.protocols) != protocols.protocol_count
        or len(identities) != protocols.protocol_count
        or not all(row.paper_role and row.safety_boundary for row in protocols.protocols)
    ):
        message = "Upstream practice vocabulary differs from the pinned integration contract"
        raise ContractError(message)
    hashes = {
        name: file_digest(Path(inspect.getfile(import_module(name))))
        for name in ("formalism.models", "practice.protocols", "simulation.emergence")
    }
    return UpstreamPracticeAudit(
        "thanks_for_nothing.upstream_practice.v1",
        tuple(row.id for row in protocols.protocols),
        sha256(json.dumps(raw_protocols, sort_keys=True).encode()).hexdigest(),
        sha256(json.dumps(raw_revision, sort_keys=True).encode()).hexdigest(),
        hashes,
        revision.controls,
        bool(revision.controls) and revision.all_controls_pass and all(revision.controls.values()),
    )
