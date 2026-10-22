# Copyright (c) 2026 Daniel Ari Friedman
"""Generate current documentation facts and replay their actual producer bindings."""

from pathlib import Path

from thanks_for_nothing.artifact_checks import Gate, read_record, scholarship_keys
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.bundle import ResearchBundle, read_bundle
from thanks_for_nothing.captions import captions_complete
from thanks_for_nothing.documentation import (
    DocumentationAudit,
    DocumentationContext,
    documentation_audit,
)
from thanks_for_nothing.formalisms import FormalismRegistry
from thanks_for_nothing.illustrations import IllustrationRegistry
from thanks_for_nothing.manuscript_variables import manuscript_variables
from thanks_for_nothing.publication import load_publication


def research_summary(root: Path, output: Path, bundle: ResearchBundle) -> str:
    """Read current quantities from records rather than duplicating them in maintained guides."""
    publication = load_publication(root)
    figures = read_record(output / "reports/illustrations.json", IllustrationRegistry)
    equations = read_record(output / "reports/formalisms.json", FormalismRegistry)
    rows = [
        "# Current research facts",
        "",
        "Generated from admitted records. Maintained guides link here for current quantities.",
        "",
        "| Publication quantity | Value | Authority |",
        "| --- | --- | --- |",
        f"| Version | {publication.version} | docs/manuscript/metadata.yaml |",
        f"| Manuscript revision date | {publication.date} | docs/manuscript/metadata.yaml |",
        f"| PDF margins (mm) | {publication.pdf_margin_mm:g} | pdf-margin-mm |",
        f"| PDF footer offset (mm) | {publication.pdf_footer_offset_mm:g} | pdf-footer-offset-mm |",
        f"| PDF body font (points) | {publication.pdf_body_font_pt:g} | pdf-body-font-pt |",
        f"| Scientific figures | {len(figures.entries)} | reports/illustrations.json |",
        f"| Numbered equations | {len(equations.entries)} | reports/formalisms.json |",
        f"| Scholarship sources | {len(scholarship_keys(root))} | data/scholarship/sources.json |",
        "",
        "## Executed design and independent units",
        "",
        "Selectors distinguish independent replicates, repeated windows, episodes and decisions.",
        "",
        "| Variable | Executed value | Producer | Selector |",
        "| --- | --- | --- | --- |",
    ]
    rows.extend(
        f"| {row.name} | {row.value} | {row.source_artifact} | {row.selector} |"
        for row in manuscript_variables(bundle)
    )
    rows.extend(
        (
            "",
            "These finite synthetic experiments and software gates do not establish human effects.",
            "",
        )
    )
    return "\n".join(rows)


def write_documentation(context: DocumentationContext, bundle: ResearchBundle) -> None:
    """Write current facts before checking their linked guides against the completed output."""
    root, output = context.root, context.output
    _ = (output / "reports/research_summary.md").write_text(research_summary(root, output, bundle))
    write_record(
        output / "reports/documentation_audit.json",
        documentation_audit(root, output=output, include_rendered=context.include_rendered),
    )


def documentation_gates(context: DocumentationContext) -> tuple[Gate, ...]:
    """Replay captions, local references and the generated current-facts page independently."""
    root, output = context.root, context.output
    report = documentation_audit(root, output=output, include_rendered=context.include_rendered)
    return (
        Gate(
            "caption_completeness",
            captions_complete(root),
            "Every scientific figure has task, reading, uncertainty and scope fields.",
        ),
        Gate(
            "documentation_closure",
            report.all_pass
            and read_record(output / "reports/documentation_audit.json", DocumentationAudit) == report,
            "Indexed guides and local Markdown references match the recorded inputs.",
        ),
        Gate(
            "documentation_facts_replay",
            (output / "reports/research_summary.md").read_text()
            == research_summary(root, output, read_bundle(output)),
            "Current publication quantities and protocol settings replay from their actual producers.",
        ),
    )
