# Copyright (c) 2026 Daniel Ari Friedman
"""Build local publication products from an already admitted numerical bundle."""

from pathlib import Path

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.custody import source_tree_receipt
from thanks_for_nothing.documentation import DocumentationContext
from thanks_for_nothing.documentation_products import write_documentation
from thanks_for_nothing.figure_suite import generate_all_figures
from thanks_for_nothing.gaze_art import copy_artwork
from thanks_for_nothing.gnn_graphs import write_gnn_graphs
from thanks_for_nothing.notebooks import execute_notebook
from thanks_for_nothing.product_contracts import NOTEBOOK_NAMES
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.reporting import compose_manuscript, render_manuscript
from thanks_for_nothing.traditions import write_traditions
from thanks_for_nothing.traditions_html import render_traditions_html


def build_publication_products(
    root: Path, output: Path, bundle: ResearchBundle, *, render: bool = True, notebook: bool = True
) -> None:
    """Render figures, manuscript and companions without regenerating simulated observations."""
    reports = output / "reports"
    initial = source_tree_receipt(root)
    write_record(
        reports / "publication_build.json",
        {
            "schema": "thanks_for_nothing.publication_build.v1",
            "status": "building",
        },
    )
    _ = write_gnn_graphs(output, bundle)
    copy_artwork(root, output)
    traditions = write_traditions(root, output)
    _ = (output / "world_traditions.html").write_text(render_traditions_html(traditions))
    figures = generate_all_figures(bundle, output / "figures")
    write_record(reports / "figure_source_map.json", figures)
    manuscript = compose_manuscript(root, output, bundle)
    if render:
        _ = render_manuscript(root, output, manuscript)
    if notebook:
        analysis = load_analysis(output / "specifications")
        write_record(
            reports / "notebook_execution.json",
            tuple(
                execute_notebook(root, output, name=name, analysis=analysis) for name in NOTEBOOK_NAMES
            ),
        )
    write_documentation(DocumentationContext(root, output, render), bundle)
    if source_tree_receipt(root) != initial:
        message = "Publication source changed while products were built"
        raise ContractError(message)
    write_record(
        reports / "publication_build.json",
        {
            "schema": "thanks_for_nothing.publication_build.v1",
            "status": "complete",
            "publication_source": initial,
            "numerical_source_receipt_sha256": file_digest(output / "data/source_tree.json"),
            "scope": "Publication products generated from the supplied admitted numerical bundle",
            "rendered": render,
            "notebook_execution": "executed_in_this_build" if notebook else "not_reexecuted",
            "products": {
                str(path.relative_to(output)): file_digest(path)
                for path in sorted(output.rglob("*"))
                if path.is_file()
                and (
                    any(
                        path.is_relative_to(output / folder)
                        for folder in ("figures", "frontmatter", "gnn", "notebook", "specifications")
                    )
                    or path.name
                    in {
                        "manuscript.pdf",
                        "manuscript.html",
                        "manuscript.md",
                        "manuscript_variables.json",
                        "research_summary.md",
                        "documentation_audit.json",
                        "world_traditions.html",
                        "world_traditions.json",
                        "gnn_graphs.json",
                        "generative_models.json",
                        "figure_source_map.json",
                        "graphical_abstracts.json",
                        "gnn_model_card.json",
                        "formalisms.json",
                        "illustrations.json",
                    }
                )
            },
        },
    )
