# Copyright (c) 2026 Daniel Ari Friedman
"""Coordinate numerical generation, typed persistence, local publication and qualification."""

from pathlib import Path

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.artifacts import inventory, write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.custody import source_tree_receipt
from thanks_for_nothing.evidence import (
    preserve_specifications,
    write_bundle_evidence,
    write_source_arrays,
)
from thanks_for_nothing.publication_products import build_publication_products
from thanks_for_nothing.research_execution import generate_research
from thanks_for_nothing.standalone_gnn import generative_run
from thanks_for_nothing.validation import ValidationReport, require_valid, validate_project


def run_pipeline(  # noqa: PLR0913 - explicit independent output and admission options
    root: Path,
    output: Path,
    *,
    replicates: int | None = None,
    render: bool = True,
    notebook: bool = True,
    specification_dir: Path | None = None,
) -> ValidationReport:
    """Require fixed-source scientific, publication and replay stages to complete successfully."""
    initial_tree = source_tree_receipt(root)
    data, reports = output / "data", output / "reports"
    data.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    specifications = output / "specifications"
    preserve_specifications(specification_dir, specifications)
    write_record(data / "source_tree.json", initial_tree)
    with generative_run(output) as generative:
        research = generate_research(root, specifications, replicates=replicates)
    write_source_arrays(data / "source_reconstruction.npz", research.reconstruction)
    write_record(data / "learning_parameters.json", research.parameters)
    write_bundle_evidence(data, research.bundle, load_analysis(specifications))
    generative.write()
    build_publication_products(root, output, research.bundle, render=render, notebook=notebook)
    if source_tree_receipt(root) != initial_tree:
        message = "Research inputs changed during pipeline execution"
        raise ContractError(message)
    write_record(reports / "artifact_manifest.json", inventory(output))
    report = validate_project(
        root, output, require_render=render, require_notebook=notebook, specification_dir=specifications
    )
    write_record(reports / "validation.json", report)
    require_valid(report)
    return report
