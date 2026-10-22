# Copyright (c) 2026 Daniel Ari Friedman
"""Typed caption authoring shared by manuscript composition and completeness checks."""

import re
from pathlib import Path
from typing import ClassVar, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.visual_tokens import REQUIRED_FIGURES


class ScientificCaption(BaseModel):
    """A complete authored explanation, resolved against the executed experiment."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True, extra="forbid", str_strip_whitespace=True
    )
    figure: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    title: str = Field(min_length=1)
    task: str = Field(min_length=1)
    reading: str = Field(min_length=1)
    uncertainty: str = Field(min_length=1)
    scope: str = Field(min_length=1)

    @property
    def token(self) -> str:
        """Identify the caption independently of its generated figure number."""
        return "{{CAPTION_" + self.figure.upper() + "}}"

    @property
    def text(self) -> str:
        """Keep all interpretive fields in both publication formats."""
        return f"{self.title} {self.task} {self.reading} {self.uncertainty} {self.scope}"


class CaptionCatalog(BaseModel):
    """The versioned, unique figure-caption authoring boundary."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["thanks_for_nothing.captions.v1"] = Field(alias="schema")
    captions: tuple[ScientificCaption, ...]


def load_captions(root: Path) -> CaptionCatalog:
    """Admit every required field and reject duplicate figure identities."""
    catalog = CaptionCatalog.model_validate(
        yaml.safe_load((root / "docs/manuscript/captions.yaml").read_text())
    )
    if len(catalog.captions) != len({caption.figure for caption in catalog.captions}):
        message = "Duplicate scientific caption identity"
        raise ContractError(message)
    return catalog


def expand_captions(source: str, catalog: CaptionCatalog) -> str:
    """Expand authored captions before numerical-token discovery and literal admission."""
    result = source
    for caption in catalog.captions:
        result = result.replace(caption.token, caption.text)
    if re.search(r"\{\{CAPTION_[A-Z0-9_]+\}\}", result):
        message = "Unknown scientific caption identity"
        raise ContractError(message)
    return result


def captions_complete(root: Path) -> bool:
    """Require one catalog caption for each figure in the authored manuscript."""
    catalog = load_captions(root)
    source = "\n".join(
        (root / "docs/manuscript" / name).read_text() for name in ("manuscript.md", "supplement.md")
    )
    images = tuple(re.finditer(r"!\[(.+)\]\(output/figures/([a-z0-9_]+)\.png\)", source))
    return (
        frozenset(c.figure for c in catalog.captions) == REQUIRED_FIGURES
        and len(images) == len(REQUIRED_FIGURES)
        and all(m[1] == "{{CAPTION_" + m[2].upper() + "}}" for m in images)
        and len({m[2] for m in images}) == len(images)
    )
