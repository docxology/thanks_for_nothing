# Copyright (c) 2026 Daniel Ari Friedman
"""Restore compressed publication records without replacing a mismatched local result."""

import gzip
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.provenance import file_digest


class RetainedRecord(BaseModel):
    """Content identities for a compressed record and its exact expanded bytes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    name: str = Field(pattern=r"^[a-z_]+\.json$")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    gzip_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def restore_records(directory: Path, records: tuple[RetainedRecord, ...]) -> None:
    """Admit both transport and content hashes before atomic, exclusive installation."""
    for record in records:
        target = directory / record.name
        archive = target.with_suffix(".json.gz")
        if target.is_symlink() or archive.is_symlink() or file_digest(archive) != record.gzip_sha256:
            message = f"Retained record transport failed admission: {record.name}"
            raise ContractError(message)
        content = gzip.decompress(archive.read_bytes())
        if sha256(content).hexdigest() != record.sha256:
            message = f"Retained record content failed admission: {record.name}"
            raise ContractError(message)
        if target.exists():
            if not target.is_file() or file_digest(target) != record.sha256:
                message = f"Existing retained record differs; preserved: {record.name}"
                raise ContractError(message)
            continue
        with TemporaryDirectory(prefix="tfn-restore-", dir=directory) as temporary:
            restored = Path(temporary) / record.name
            _ = restored.write_bytes(content)
            target.hardlink_to(restored)
