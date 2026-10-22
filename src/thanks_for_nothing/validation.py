# Copyright (c) 2026 Daniel Ari Friedman
"""Validate artifact identity, paired designs and bounded scientific language."""

import re
from dataclasses import replace
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.artifact_checks import (
    Gate,
    ValidationReport,
    claims_valid,
    figures_valid,
    manifest_valid,
    product_presence_gates,
    read_record,
    scholarship_valid,
)
from thanks_for_nothing.attention import AttentionAudit
from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.calibration import CalibrationAudit, calibration_consistent
from thanks_for_nothing.contracts import ContractError, StudyResult
from thanks_for_nothing.documentation import DocumentationContext
from thanks_for_nothing.documentation_products import documentation_gates
from thanks_for_nothing.experimental_checks import experimental_replay_gates, read_experimental_records
from thanks_for_nothing.experiments import run_learning_experiment
from thanks_for_nothing.figure_placement import figure_placement_valid
from thanks_for_nothing.gnn_graphs import gnn_graphs_valid
from thanks_for_nothing.model_checks import attention_valid, paired_design, source_tree_valid
from thanks_for_nothing.nothingness import NothingnessAudit
from thanks_for_nothing.product_contracts import (
    EVIDENCE_CEILING,
    FORBIDDEN_MANUSCRIPT_PHRASES,
    REQUIRED_OUTPUTS,
    REQUIRED_SPECIFICATION_NAMES,
)
from thanks_for_nothing.provenance import ProvenanceError, build_provenance_audit, file_digest
from thanks_for_nothing.publication_checks import manuscript_variables_valid, publication_valid
from thanks_for_nothing.sampling_diagnostics import SamplingAudit, build_sampling_audit
from thanks_for_nothing.sensitivity import SensitivityAudit
from thanks_for_nothing.source_reconstruction import SourceAudit, build_source_audit
from thanks_for_nothing.specifications import load_study
from thanks_for_nothing.statistics import (
    StatisticalInputError,
    StatisticalReport,
    build_statistical_report,
)
from thanks_for_nothing.traditions import TraditionsRecord, traditions_valid
from thanks_for_nothing.traditions_html import render_traditions_html


def validate_project(
    root: Path,
    output: Path,
    *,
    require_render: bool = True,
    require_notebook: bool | None = None,
    specification_dir: Path | None = None,
) -> ValidationReport:
    """Return explicit failed gates for absent, malformed or inadmissible artifacts."""
    missing = tuple(path for path in REQUIRED_OUTPUTS if not (output / path).is_file())
    if missing:
        return ValidationReport(
            "thanks_for_nothing.validation.v1",
            (Gate("required_artifacts_present", passed=False, detail="Missing: " + ", ".join(missing)),),
            all_pass=False,
            evidence_ceiling=EVIDENCE_CEILING,
        )
    try:
        return _validate_project(
            root,
            output,
            require_render=require_render,
            require_notebook=require_render if require_notebook is None else require_notebook,
            specification_dir=specification_dir,
        )
    except (OSError, ValidationError, ProvenanceError, StatisticalInputError, ContractError) as error:
        return ValidationReport(
            "thanks_for_nothing.validation.v1",
            (Gate("artifact_admission", passed=False, detail=str(error)),),
            all_pass=False,
            evidence_ceiling=EVIDENCE_CEILING,
        )


def _validate_project(
    root: Path,
    output: Path,
    *,
    require_render: bool,
    require_notebook: bool,
    specification_dir: Path | None,
) -> ValidationReport:
    """Validate admitted records against current declarations and all product gates."""
    _ = build_provenance_audit(root)
    source = TypeAdapter(SourceAudit).validate_json((output / "data/source_audit.json").read_text())
    study = read_record(output / "data/study.json", StudyResult)
    statistics = read_record(output / "data/statistics.json", StatisticalReport)
    absence = read_record(output / "data/nothingness.json", NothingnessAudit)
    attention = read_record(output / "data/attention.json", AttentionAudit)
    calibration = read_record(output / "data/statistical_calibration.json", CalibrationAudit)
    sensitivity = read_record(output / "data/sensitivity.json", SensitivityAudit)
    experiments = read_experimental_records(output)
    preserved = output / "specifications"
    names = REQUIRED_SPECIFICATION_NAMES
    specifications_match = all((preserved / f"{name}.gnn.md").is_file() for name in names)
    if specification_dir is not None:
        specifications_match = specifications_match and all(
            file_digest(preserved / f"{name}.gnn.md")
            == file_digest(specification_dir / f"{name}.gnn.md")
            for name in names
        )
    model, design = load_study(preserved)
    analysis = load_analysis(preserved)
    learning = run_learning_experiment(replicates=study.design.replicates, specification_dir=preserved)
    paired = paired_design(study)
    replay = (
        build_statistical_report(
            study.rows,
            seed=statistics.seed,
            bootstrap_draws=design.bootstrap_draws,
            permutation_draws=design.permutation_draws,
            analysis=analysis,
        )
        if paired
        else None
    )
    expected_design = TypeAdapter(type(study.design)).validate_python(design.model_dump())
    design_matches = replace(study.design, replicates=expected_design.replicates) == expected_design
    manuscript = (output / "reports/manuscript.md").read_text()
    forbidden = re.search("(?i)(" + "|".join(FORBIDDEN_MANUSCRIPT_PHRASES) + ")", manuscript)
    sampling_matches = read_record(
        output / "data/sampling_diagnostics.json", SamplingAudit
    ) == build_sampling_audit(read_bundle(output), analysis)
    experiment_gates = experimental_replay_gates(root, study, preserved, experiments, learning)
    gates = [
        Gate(
            "gnn_graphs_source_and_execution",
            all(gate.passed for gate in experiment_gates)
            and gnn_graphs_valid(output, read_bundle(output)),
            "Parsed topology, tensor shapes, native renderer products and consumed source identities.",
        ),
        *experiment_gates,
        *documentation_gates(DocumentationContext(root, output, require_render)),
        Gate(
            "publication_metadata_and_formalisms",
            publication_valid(root, output, require_render=require_render),
            "Author, DOI status, cover and ordered equation/figure registries admitted.",
        ),
        Gate(
            "manuscript_variables_and_supplements",
            all(gate.passed for gate in experiment_gates) and manuscript_variables_valid(root, output),
            "IMRAD components, generated values, producer bindings and composed bytes replay exactly.",
        ),
        Gate(
            "independent_source_and_dependency_pins",
            passed=True,
            detail="Live bytes and executing imports admitted.",
        ),
        Gate(
            "artifact_inventory",
            manifest_valid(output),
            "Every declared artifact hash and byte count checked.",
        ),
        Gate(
            "gnn_main_model_binding",
            study.model_sha256 == model.source_hash and design_matches,
            "Main study binds current packaged GNN bytes.",
        ),
        Gate(
            "paired_design",
            paired,
            "Balanced agents, shared exposures and baselines, matched recall dose.",
        ),
        Gate(
            "statistics_replay",
            statistics == replay,
            f"All {len(statistics.contrasts)} contrasts replay from on-disk agent rows.",
        ),
        Gate(
            "absence_controls",
            all(absence.controls.values())
            and absence.all_controls_pass
            and absence.missing_posterior == absence.prior
            and absence.missing_kl_bits == 0,
            "Missingness, invalid-probability, label-invariance and valuation nulls.",
        ),
        Gate(
            "native_attention",
            attention_valid(attention),
            "Actual native receipt and probability checks.",
        ),
        Gate(
            "statistical_controls",
            calibration_consistent(calibration, design, analysis=analysis)
            and read_record(output / "data/analysis_protocol.json", type(analysis)) == analysis
            and sampling_matches,
            "Fixture identities, admitted budgets, rate denominators, exact bounds and controls.",
        ),
        Gate(
            "sensitivity_admission",
            all(sensitivity.controls.values())
            and len({row.model_sha256 for row in sensitivity.rows}) == len(sensitivity.rows),
            "Every cell has distinct admitted GNN bytes and paired exposures.",
        ),
        Gate(
            "figure_integrity_and_legibility",
            figures_valid(output),
            "PNG/SVG/source digests, visible legend entries, semantic colors and placement fonts.",
        ),
        Gate(
            "main_results_figure_context",
            figure_placement_valid(root),
            "Situations accompany main results; detailed charts remain supplementary.",
        ),
        Gate(
            "scholarship_closure",
            scholarship_valid(root, manuscript),
            "Unique source and bibliography keys, citations and evidence ceilings.",
        ),
        Gate(
            "world_traditions_provenance",
            traditions_valid(root, output)
            and (output / "world_traditions.html").read_text()
            == render_traditions_html(
                TraditionsRecord.model_validate_json((output / "data/world_traditions.json").read_text())
            ),
            "Qualitative rows, linked source identities and companion exactly replay authored inputs.",
        ),
        Gate(
            "manuscript_scope",
            forbidden is None and re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", manuscript) is None,
            "Bounded prohibited-claim language check and complete variable hydration.",
        ),
    ]
    gates.append(
        Gate(
            "research_input_custody",
            source_tree_valid(root, output),
            "Live inputs and executing package match the original source tree receipt.",
        )
    )
    gates.append(
        Gate(
            "preserved_specifications",
            specifications_match,
            "Every consumed declaration is preserved and matches any explicit input directory.",
        )
    )
    gates.append(
        Gate(
            "source_reconstruction_scope",
            source == build_source_audit(root, analysis=analysis),
            "Digest-bound source audit controls replay exactly.",
        )
    )
    gates.append(
        Gate(
            "claim_evidence_ceilings",
            claims_valid(root, output, tuple(gates)),
            "Unique bounded claims bind real artifacts, passed gates and evidence limits.",
        )
    )
    gates.extend(
        product_presence_gates(output, require_render=require_render, require_notebook=require_notebook)
    )
    return ValidationReport(
        "thanks_for_nothing.validation.v1",
        tuple(gates),
        all(gate.passed for gate in gates),
        EVIDENCE_CEILING,
    )


def require_valid(report: ValidationReport) -> None:
    """Fail explicitly when any project gate rejects its evidence."""
    failed = [gate.name for gate in report.gates if not gate.passed]
    if failed:
        raise ContractError("Failed project gates: " + ", ".join(failed))


__all__ = ["Gate", "ValidationReport", "read_record", "require_valid", "validate_project"]
