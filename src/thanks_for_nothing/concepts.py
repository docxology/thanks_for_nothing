# Copyright (c) 2026 Daniel Ari Friedman
"""Shared editorial vocabulary; numerical model choices remain in admitted GNN resources."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final, Literal

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_variables import ManuscriptVariable


@dataclass(frozen=True, slots=True)
class NothingConcept:
    """One explicitly bounded use of nothing, shared by prose and scientific figures."""

    code: Literal["A", "B", "C", "D"]
    name: str
    role: str
    meaning: str
    operation: str
    boundary: str

    @property
    def label(self) -> str:
        """Keep the Figure 1 identifier attached to the same concept everywhere."""
        return f"{self.code}: {self.name}"


OBSERVED_ABSENCE: Final = NothingConcept(
    "A",
    "Observed absence",
    "positive_recall",
    "A working channel records no event.",
    "Update with the no-event likelihood.",
    "Detection and exposure assumptions matter.",
)
MISSING_OBSERVATION: Final = NothingConcept(
    "B",
    "Missing observation",
    "no_recall",
    "An observation record is unavailable.",
    "Retain the prior under our missingness rule.",
    "State-dependent missingness needs its own model.",
)
COUNTERFACTUAL_VALUE: Final = NothingConcept(
    "C",
    "Counterfactual value",
    "absence_appreciation",
    "Actuality is compared with a specified alternative.",
    "Assign value without adding an observation.",
    "Reference-dependent value is not new evidence.",
)
NON_REIFICATION: Final = NothingConcept(
    "D",
    "Non-reification",
    "matched_random_recall",
    "A useful distinction is not held as intrinsically fixed.",
    "Examine its conditions; retain or revise its use.",
    "Finite revisability does not measure realizing emptiness.",
)
CONCEPTS: Final = (
    OBSERVED_ABSENCE,
    MISSING_OBSERVATION,
    COUNTERFACTUAL_VALUE,
    NON_REIFICATION,
)


def concept_variables(output: Path) -> tuple[ManuscriptVariable, ...]:
    """Inject the exact shared names and reading guide with a serialized source binding."""
    source = (output / "data/concepts.json").read_bytes()
    if source != record_json(CONCEPTS).encode():
        message = "Concept vocabulary differs from the canonical registry"
        raise ContractError(message)
    digest = sha256(source).hexdigest()
    table = [
        "| Concept | Operation in this project | Evidential boundary |",
        "| --- | --- | --- |",
        *(f"| **{item.label}** | {item.operation} | {item.boundary} |" for item in CONCEPTS),
    ]
    values = [
        ManuscriptVariable("CONCEPT_COUNT", str(len(CONCEPTS)), "data/concepts.json", digest, "length"),
        ManuscriptVariable(
            "CONCEPT_GUIDE_TABLE", "\n".join(table), "data/concepts.json", digest, "all definitions"
        ),
    ]
    for index, item in enumerate(CONCEPTS):
        for field, value in (("NAME", item.name.lower()), ("LABEL", item.label)):
            values.append(
                ManuscriptVariable(
                    f"CONCEPT_{item.code}_{field}",
                    value,
                    "data/concepts.json",
                    digest,
                    f"lower(/{index}/name)"
                    if field == "NAME"
                    else f"/{index}/code + ': ' + /{index}/name",
                )
            )
    return tuple(values)
