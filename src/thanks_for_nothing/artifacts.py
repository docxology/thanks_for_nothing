# Copyright (c) 2026 Daniel Ari Friedman
"""Serialize typed research records and inventory their exact output bytes."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import TypeVar

from pydantic import TypeAdapter

Record = TypeVar("Record")


@dataclass(frozen=True, slots=True)
class Artifact:
    """One output file bound to its relative path, digest and byte count."""

    path: str
    sha256: str
    bytes: int


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    """Inventory excluding self-referential manifest and validation receipts."""

    schema: str
    artifacts: tuple[Artifact, ...]


def record_json(record: Record, *, record_type: type[Record] | None = None) -> str:
    """Serialize a dataclass or mapping, optionally using an explicit schema."""
    adapter: TypeAdapter[Record] = TypeAdapter(record_type or type(record))
    return adapter.dump_json(record, indent=2).decode() + "\n"


def write_record(path: Path, record: Record, *, record_type: type[Record] | None = None) -> None:
    """Write UTF-8 JSON through the same typed serialization boundary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(record_json(record, record_type=record_type), encoding="utf-8")


def inventory(output: Path) -> ArtifactManifest:
    """Hash every regular output except the two self-referential receipts."""
    excluded = {"artifact_manifest.json", "validation.json"}
    return ArtifactManifest(
        "thanks_for_nothing.artifacts.v1",
        tuple(
            Artifact(
                str(path.relative_to(output)), sha256(path.read_bytes()).hexdigest(), path.stat().st_size
            )
            for path in sorted(output.rglob("*"))
            if path.is_file() and path.name not in excluded
        ),
    )
