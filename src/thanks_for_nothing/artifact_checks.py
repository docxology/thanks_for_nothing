# Copyright (c) 2026 Daniel Ari Friedman
"""Validate artifact identity, paired designs and bounded scientific language."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, ClassVar, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, TypeAdapter, ValidationError

from thanks_for_nothing.artifacts import ArtifactManifest
from thanks_for_nothing.figure_checks import figures_valid
from thanks_for_nothing.product_contracts import MIN_RENDER_BYTES, NOTEBOOK_NAMES
from thanks_for_nothing.provenance import file_digest

__all__ = [
    "Gate",
    "ValidationReport",
    "claims_valid",
    "figures_valid",
    "manifest_valid",
    "product_presence_gates",
    "read_record",
    "scholarship_valid",
]

Record = TypeVar("Record")


class _ScholarshipSource(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    key: str
    evidence_ceiling: str
    url: str


class _Scholarship(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    sources: tuple[_ScholarshipSource, ...]


Nonempty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class _Claim(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    id: Nonempty
    claim: Nonempty
    kind: Literal["source_reconstruction", "synthetic_model", "software_validation", "finite_comparator"]
    source_role: Nonempty
    artifact: Nonempty
    gate: Nonempty
    evidence_ceiling: Nonempty
    prohibited_inference: Nonempty
    future_evidence: Nonempty
    boundary_stressor: Nonempty


class _ClaimContract(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["thanks_for_nothing.claim_contract.v1"] = Field(alias="schema")
    claims: Annotated[tuple[_Claim, ...], Field(min_length=1)]


@dataclass(frozen=True, slots=True)
class Gate:
    """One independently observed project acceptance condition."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Named project gates and an explicit finite-model evidence ceiling."""

    schema: str
    gates: tuple[Gate, ...]
    all_pass: bool
    evidence_ceiling: str


def product_presence_gates(
    output: Path, *, require_render: bool, require_notebook: bool
) -> tuple[Gate, ...]:
    """Check the requested rendered and executed products against the artifact size contract."""
    gates: list[Gate] = []
    rendered_paths = ("manuscript.pdf", "manuscript.html")
    notebook_paths = tuple(
        path
        for name in NOTEBOOK_NAMES
        for path in (
            f"notebook/{name}.executed.ipynb",
            f"notebook/{name}.html",
        )
    )
    for required, name, paths in (
        (require_render, "rendered_products_present", rendered_paths),
        (require_notebook, "executed_notebook_present", notebook_paths),
    ):
        if required:
            present = all(
                (output / path).is_file() and (output / path).stat().st_size > MIN_RENDER_BYTES
                for path in paths
            )
            gates.append(
                Gate(name, present, "Required products exist; visual inspection is recorded separately.")
            )
    return tuple(gates)


def read_record(path: Path, record_type: type[Record]) -> Record:
    """Parse a JSON artifact into its declared typed boundary."""
    adapter: TypeAdapter[Record] = TypeAdapter(record_type)
    return adapter.validate_json(path.read_text())


def manifest_valid(output: Path) -> bool:
    """Check complete inventory membership, safe paths, byte counts and hashes."""
    manifest = read_record(output / "reports/artifact_manifest.json", ArtifactManifest)
    declared = {item.path for item in manifest.artifacts}
    actual = {
        str(path.relative_to(output))
        for path in output.rglob("*")
        if path.is_file() and path.name not in {"artifact_manifest.json", "validation.json"}
    }
    if declared != actual or len(declared) != len(manifest.artifacts):
        return False
    for item in manifest.artifacts:
        path = (output / item.path).resolve()
        if not path.is_relative_to(output.resolve()) or not path.is_file():
            return False
        if file_digest(path) != item.sha256 or path.stat().st_size != item.bytes:
            return False
    return True


def scholarship_keys(root: Path) -> tuple[str, ...]:
    """Expose admitted catalog identities for generated documentation quantities."""
    catalog = _Scholarship.model_validate_json((root / "data/scholarship/sources.json").read_text())
    return tuple(source.key for source in catalog.sources)


def scholarship_valid(root: Path, manuscript: str) -> bool:
    """Require citation closure and a unique source inventory."""
    catalog = _Scholarship.model_validate_json((root / "data/scholarship/sources.json").read_text())
    keys = [row.key for row in catalog.sources]
    bibliography = (root / "docs/manuscript/references.bib").read_text()
    bibkeys = re.findall(r"@\w+\{([^,]+),", bibliography)
    cited = set(re.findall(r"(?<![\w/])@([A-Za-z][\w:-]*)", manuscript))
    return (
        len(keys) == len(set(keys))
        and len(bibkeys) == len(set(bibkeys))
        and set(keys) == set(bibkeys)
        and cited <= set(keys)
        and all(row.evidence_ceiling and row.url.startswith("https://") for row in catalog.sources)
    )


def claims_valid(root: Path, output: Path, gates: tuple[Gate, ...]) -> bool:
    """Admit only bounded claim kinds with real artifacts and satisfied named gates."""
    try:
        catalog = _ClaimContract.model_validate_json((root / "data/claim_contract.json").read_text())
    except ValidationError:
        return False
    if len({claim.id for claim in catalog.claims}) != len(catalog.claims):
        return False
    passed = {gate.name for gate in gates if gate.passed}
    for claim in catalog.claims:
        path = (output / claim.artifact).resolve()
        if not path.is_relative_to(output.resolve()) or not path.is_file() or claim.gate not in passed:
            return False
    return True
