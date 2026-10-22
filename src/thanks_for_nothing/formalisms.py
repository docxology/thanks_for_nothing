# Copyright (c) 2026 Daniel Ari Friedman
"""Bind automatically numbered display formalisms to stable authored labels."""

import re
from dataclasses import dataclass
from hashlib import sha256

from thanks_for_nothing.contracts import ContractError


@dataclass(frozen=True, slots=True)
class Formalism:
    """Document order and expression identity, independent of hardcoded equation numbers."""

    number: int
    label: str
    expression_sha256: str


@dataclass(frozen=True, slots=True)
class FormalismRegistry:
    """The display equations expected in both PDF and HTML."""

    schema: str
    entries: tuple[Formalism, ...]


def build_formalism_registry(manuscript: str) -> FormalismRegistry:
    """Require paired display delimiters, one unique label, and resolved equation links."""
    expressions = [match.group(1) for match in re.finditer(r"(?ms)^\$\$\n(.*?)^\$\$", manuscript)]
    if sum(line.strip() == "$$" for line in manuscript.splitlines()) != 2 * len(expressions):
        message = "Unpaired display-formalism delimiter"
        raise ContractError(message)
    entries: list[Formalism] = []
    for index, expression in enumerate(expressions, 1):
        if re.search(r"\\(?:tag\*?|eqno|leqno)\b", expression):
            message = "Display formalism numbers must be generated, not authored"
            raise ContractError(message)
        labels = [match.group(1) for match in re.finditer(r"\\label\{(eq:[A-Za-z0-9_-]+)\}", expression)]
        if len(labels) != 1:
            message = "Each display formalism requires exactly one eq: label"
            raise ContractError(message)
        body = re.sub(r"\\label\{eq:[A-Za-z0-9_-]+\}", "", expression).strip()
        entries.append(Formalism(index, labels[0], sha256(body.encode()).hexdigest()))
    names = {entry.label for entry in entries}
    references = set(re.findall(r"\]\(#(eq:[A-Za-z0-9_-]+)\)", manuscript))
    if len(names) != len(entries) or not references <= names:
        message = "Duplicate or unresolved formalism identifier"
        raise ContractError(message)
    return FormalismRegistry("thanks_for_nothing.formalisms.v1", tuple(entries))
