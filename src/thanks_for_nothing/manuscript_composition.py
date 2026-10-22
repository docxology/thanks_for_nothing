# Copyright (c) 2026 Daniel Ari Friedman
"""Replayable publication composition with exact template and producer bindings."""

import json
import os
import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.captions import expand_captions, load_captions
from thanks_for_nothing.concepts import concept_variables
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_literals import require_injected_numbers
from thanks_for_nothing.manuscript_quantities import additional_variables
from thanks_for_nothing.manuscript_references import (
    calibration_variables,
    historical_variables,
    source_array_variables,
)
from thanks_for_nothing.manuscript_variables import (
    ManuscriptVariable,
    manuscript_variables,
    model_variables,
    parameter_table,
)
from thanks_for_nothing.provenance import file_digest


@dataclass(frozen=True, slots=True)
class TemplateBinding:
    """One authored manuscript component, distinguished from generated publication text."""

    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class FindingBinding:
    """A generated block bound to the entire admitted research bundle."""

    name: str
    value_sha256: str


@dataclass(frozen=True, slots=True)
class ManuscriptLedger:
    """Exact replay contract for main text, supplements, scalar values and generated findings."""

    schema: str
    templates: tuple[TemplateBinding, ...]
    bundle_sha256: str
    variables: tuple[ManuscriptVariable, ...]
    findings: tuple[FindingBinding, ...]
    main_sections: tuple[str, ...]
    composed_sha256: str


def _bound_variables(
    root: Path, output: Path, bundle: ResearchBundle, used: set[str]
) -> tuple[ManuscriptVariable, ...]:
    variables = manuscript_variables(bundle) + additional_variables(output, bundle, used)
    if any(name.startswith("CONCEPT_") for name in used):
        variables += concept_variables(output)
    if used & {"SOURCE_AFTER_POSITIVE", "SOURCE_AFTER_NEGATIVE", "DESTENO_PARTICIPANTS"}:
        variables += historical_variables(root)
    if used & {"CALIBRATION_FIXTURE_SETTINGS", "CALIBRATION_FIXTURES"}:
        variables += calibration_variables()
    if "SOURCE_BELIEF_AGENTS" in used:
        variables += source_array_variables(output)
    if any(name.startswith("MODEL_") for name in used):
        variables += model_variables(bundle, output / "specifications")
    return variables


def compose_source(
    root: Path, output: Path, bundle: ResearchBundle, findings: dict[str, str]
) -> tuple[str, ManuscriptLedger]:
    """Admit the IMRAD/supplement boundary and resolve every changing manuscript value."""
    main = root / "docs/manuscript/manuscript.md"
    source = main.read_text()
    templates = [TemplateBinding(str(main.relative_to(root)), file_digest(main))]
    headings = tuple(
        match.group(1).strip() for match in re.finditer(r"^# ([^{\n]+)", source, flags=re.MULTILINE)
    )
    if "{{SUPPLEMENT}}" in source:
        if source.count("{{SUPPLEMENT}}") != 1 or headings != (
            "Abstract",
            "Introduction",
            "Methods",
            "Results",
            "Discussion",
            "References",
        ):
            message = "Main manuscript must use one supplement and the complete IMRAD sequence"
            raise ContractError(message)
        supplement = root / "docs/manuscript/supplement.md"
        templates.append(TemplateBinding(str(supplement.relative_to(root)), file_digest(supplement)))
        source = source.replace("{{SUPPLEMENT}}", supplement.read_text())
    if "{{CAPTION_" in source:
        caption_source = root / "docs/manuscript/captions.yaml"
        templates.append(
            TemplateBinding(str(caption_source.relative_to(root)), file_digest(caption_source))
        )
        source = expand_captions(source, load_captions(root))
    require_injected_numbers(source)
    used = {match.group(1) for match in re.finditer(r"\{\{([A-Z][A-Z0-9_]*)\}\}", source)}
    variables = _bound_variables(root, output, bundle, used)
    if len(variables) != len({row.name for row in variables}):
        message = "Duplicate manuscript variable names"
        raise ContractError(message)
    replacements = findings | {f"{{{{{row.name}}}}}": row.value for row in variables}
    replacements["{{PARAMETER_TABLE}}"] = parameter_table(variables)
    for token, value in replacements.items():
        source = source.replace(token, value)
    if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", source):
        message = "Unresolved manuscript variable"
        raise ContractError(message)
    relative_figures = os.path.relpath(output / "figures", root)
    source = source.replace("output/figures/", relative_figures + "/")
    source = source.replace("output/world_traditions.html", "world_traditions.html")
    scalar_names = {row.name for row in variables}
    ledger = ManuscriptLedger(
        "thanks_for_nothing.manuscript_variables.v1",
        tuple(templates),
        sha256(
            json.dumps(
                TypeAdapter(JsonValue).validate_json(record_json(bundle)),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode()
        ).hexdigest(),
        tuple(row for row in variables if row.name in used),
        tuple(
            FindingBinding(name, sha256(replacements[f"{{{{{name}}}}}"].encode()).hexdigest())
            for name in sorted(used - scalar_names)
        ),
        headings,
        sha256(source.encode()).hexdigest(),
    )
    return source, ledger
