# Copyright (c) 2026 Daniel Ari Friedman
"""Admit scientific figure identities and document-order references."""

import re
from dataclasses import dataclass
from hashlib import sha256

from thanks_for_nothing.contracts import ContractError


@dataclass(frozen=True, slots=True)
class Illustration:
    """An authored caption, stable anchor and image path, with a generated ordinal."""

    number: int
    label: str
    image_path: str
    caption_sha256: str


@dataclass(frozen=True, slots=True)
class IllustrationRegistry:
    """Scientific figures in the manuscript body; conceptual cover art is separate."""

    schema: str
    entries: tuple[Illustration, ...]


def build_illustration_registry(manuscript: str) -> IllustrationRegistry:
    """Require dedicated, labeled image blocks and resolved figure references."""
    matches = tuple(
        re.finditer(
            r"(?m)^!\[(.+)\]\(([^)\n]+)\)\{#(fig-[A-Za-z0-9_-]+)[^}\n]*\}\s*$",
            manuscript,
        )
    )
    if len(matches) != len(re.findall(r"!\[", manuscript)):
        message = "Scientific figures require one-line caption blocks with fig- identifiers"
        raise ContractError(message)
    if any(re.match(r"Figure\s+\d+\b", match.group(1)) for match in matches):
        message = "Figure numbers must be generated, not authored"
        raise ContractError(message)
    entries = tuple(
        Illustration(index, match.group(3), match.group(2), sha256(match.group(1).encode()).hexdigest())
        for index, match in enumerate(matches, 1)
    )
    labels = {entry.label for entry in entries}
    references = set(re.findall(r"\]\(#(fig-[A-Za-z0-9_-]+)\)", manuscript))
    if len(labels) != len(entries) or not references <= labels:
        message = "Duplicate or unresolved figure identifier"
        raise ContractError(message)
    return IllustrationRegistry("thanks_for_nothing.illustrations.v1", entries)
