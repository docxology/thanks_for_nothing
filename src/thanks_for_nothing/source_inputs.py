# Copyright (c) 2026 Daniel Ari Friedman
"""Shared typed notebook parsing and strict source-path resolution."""

from pathlib import Path
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict

Array = NDArray[np.float64]


class SourceInputError(ValueError):
    """A source identity or numerical-run boundary violation."""


class NotebookCell(BaseModel):
    """The preserved source text of a notebook cell."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    source: tuple[str, ...]


class Notebook(BaseModel):
    """Typed notebook source boundary, excluding cached execution output."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    cells: tuple[NotebookCell, ...]


def source_bytes(root: Path | None, filename: str) -> bytes:
    """Resolve explicit roots strictly, or bundled wheel sources before checkout data."""
    if root is not None:
        path = root / "data" / "sources" / filename
    else:
        packaged = Path(__file__).resolve().parent / "resources" / "sources" / filename
        path = (
            packaged
            if packaged.is_file()
            else Path(__file__).resolve().parents[2] / "data" / "sources" / filename
        )
    try:
        return path.read_bytes()
    except FileNotFoundError as error:
        message = (
            f"Source notebook missing at {path}; "
            "acquire the separately licensed inputs with scripts/acquire_external_inputs.py "
            "and supply root containing data/sources (see docs/external-inputs.md)"
        )
        raise SourceInputError(message) from error
