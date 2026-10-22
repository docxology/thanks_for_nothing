# Copyright (c) 2026 Daniel Ari Friedman
"""Acquire omitted research inputs explicitly without weakening their digest admission."""

import shutil
import subprocess
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.provenance import file_digest


class ExternalInput(BaseModel):
    """A separately acquired file, its original-host URL and required content identity."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    url: str = Field(pattern=r"^https://")


class ExternalInputs(BaseModel):
    """The declarative acquisition inventory; it grants no redistribution rights."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["thanks_for_nothing.external_inputs.v1"] = Field(alias="schema")
    inputs: tuple[ExternalInput, ...] = Field(min_length=1)


def acquire_external_inputs(root: Path, manifest: Path) -> tuple[Path, ...]:
    """Reuse exact files, refuse mismatches, and admit downloads before exclusive creation."""
    inventory = ExternalInputs.model_validate_json(manifest.read_text())
    curl = shutil.which("curl")
    if curl is None:
        message = "curl is required for explicit external-input acquisition"
        raise ContractError(message)
    root = root.resolve()
    paths: list[Path] = []
    for item in inventory.inputs:
        relative = PurePosixPath(item.path)
        target = root / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or not relative.parts
            or target.is_symlink()
            or not target.resolve().is_relative_to(root)
            or target in paths
        ):
            message = f"External input path is unsafe or duplicated: {item.path}"
            raise ContractError(message)
        paths.append(target)
    for item, target in zip(inventory.inputs, paths, strict=True):
        if target.exists():
            if not target.is_file() or file_digest(target) != item.sha256:
                message = f"Existing external input differs; preserved without replacement: {item.path}"
                raise ContractError(message)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="tfn-acquire-", dir=target.parent) as temporary:
            download = Path(temporary) / "download"
            _ = subprocess.run(  # noqa: S603 - fixed curl executable and separate arguments, no shell
                [
                    curl, "--fail", "--location", "--retry", "2", "--retry-all-errors",
                    "--connect-timeout", "15", "--max-time", "60",
                    "--proto", "=https", "--proto-redir", "=https",
                    "--output", str(download), "--url", item.url,
                ],
                check=True,
            )
            if file_digest(download) != item.sha256:
                message = f"Downloaded external input failed SHA256 admission: {item.path}"
                raise ContractError(message)
            target.hardlink_to(download)
    return tuple(paths)
