# Copyright (c) 2026 Daniel Ari Friedman
"""Reject numerical experiment claims that bypass producer-bound composition."""

import re
from dataclasses import dataclass
from typing import Final

from thanks_for_nothing.contracts import ContractError

_NUMBER: Final = re.compile(r"(?<![\w.])(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?(?!\w|\.\d)")
_PROTECTED: Final = (
    re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}"),
    re.compile(r"\[[^\]\n]*@[A-Za-z][^\]\n]*\]"),
    re.compile(r"\]\([^\n)]*\)"),
    re.compile(r"\{#[^}\n]+\}"),
    re.compile(r"\b(?:SN|MN|AN|Ud|Dhp)\s+\d+(?:[.\u2013-]\d+)*"),
    re.compile(r"(?m:^#{1,6}\s+S\d+\.)"),
)
_MATH: Final = re.compile(r"\$\$[\s\S]*?\$\$|\$[^$\n]+\$")


@dataclass(frozen=True, slots=True)
class UnboundLiteral:
    """An authored number with enough source context to correct its binding."""

    value: str
    line: int
    context: str


def unbound_literals(source: str) -> tuple[UnboundLiteral, ...]:
    """Permit cited locators and mathematical identities, never a bare cohort or result."""
    masked = list(source)
    for pattern in _PROTECTED:
        for match in pattern.finditer(source):
            masked[match.start() : match.end()] = ["\n" if c == "\n" else " " for c in match[0]]
    clean = "".join(masked)
    mathematical = tuple((m.start(), m.end()) for m in _MATH.finditer(clean))
    failures: list[UnboundLiteral] = []
    for match in _NUMBER.finditer(clean):
        inside_math = any(start <= match.start() < end for start, end in mathematical)
        prefix = clean[max(0, match.start() - 2) : match.start()]
        identity = inside_math and (
            match[0] in {"0", "1"} or (match[0] == "2" and prefix.endswith(("^", "^{")))
        )
        if not identity:
            failures.append(
                UnboundLiteral(
                    match[0],
                    source.count("\n", 0, match.start()) + 1,
                    source[max(0, match.start() - 35) : match.end() + 45].replace("\n", " "),
                )
            )
    return tuple(failures)


def require_injected_numbers(source: str) -> None:
    """Reject unbound values before generated replacements can obscure their origin."""
    failures = unbound_literals(source)
    if failures:
        details = "; ".join(f"{r.value!r} at line {r.line}: {r.context}" for r in failures)
        raise ContractError("Unbound numerical literal; use a producer variable. " + details)
