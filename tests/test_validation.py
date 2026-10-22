# Copyright (c) 2026 Daniel Ari Friedman
"""Real-file negative controls for artifact, claim and numerical validation gates."""

import json
import shutil

import pytest
from pydantic import ValidationError

from thanks_for_nothing.artifact_checks import read_record
from thanks_for_nothing.artifacts import inventory, write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.practice_contracts import PracticeAudit
from thanks_for_nothing.validation import require_valid, validate_project


@pytest.fixture
def copy_case(pipeline_case, tmp_path):
    root = tmp_path / "source"
    shutil.copytree(pipeline_case.root, root)
    return root, root / "output", root / "models"


def _validate(case):
    root, output, models = case
    return validate_project(root, output, require_render=False, specification_dir=models)


def _failed(report, name):
    assert not report.all_pass
    assert any(gate.name == name and not gate.passed for gate in report.gates)
    with pytest.raises(ContractError, match="Failed project gates"):
        require_valid(report)


def test_mutated_artifact_and_missing_required_record_reject(copy_case):
    _, output, _ = copy_case
    path = output / "data/agents.csv"
    path.write_text(path.read_text() + "corrupted\n")
    _failed(_validate(copy_case), "artifact_inventory")
    path = output / "data/study.json"
    path.rename(path.with_suffix(".absent"))
    _failed(_validate(copy_case), "required_artifacts_present")


def test_incomplete_pairs_and_stale_design_reject(copy_case):
    _, output, _ = copy_case
    path = output / "data/study.json"
    data = json.loads(path.read_text())
    data["rows"].pop()
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "paired_design")


def test_stale_figure_source_hash_rejects_even_after_inventory_refresh(copy_case):
    _, output, _ = copy_case
    path = output / "reports/figure_source_map.json"
    data = json.loads(path.read_text())
    data[0]["source_sha256"][0] = "0" * 64
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "figure_integrity_and_legibility")


@pytest.mark.parametrize(
    ("text", "gate"),
    [
        ("This demonstrates that gratitude improves health.", "manuscript_scope"),
        ("An unsupported citation [@not_a_real_key].", "scholarship_closure"),
        ("{{UNKNOWN_TOKEN}}", "manuscript_scope"),
    ],
)
def test_manuscript_scope_and_citation_rejections(copy_case, text, gate):
    _, output, _ = copy_case
    path = output / "reports/manuscript.md"
    path.write_text(path.read_text() + "\n" + text)
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), gate)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("gate", "unknown_gate"),
        ("future_evidence", ""),
        ("kind", "human_empirical"),
    ],
)
def test_claim_contract_rejects_unqualified_claims(copy_case, field, value):
    root, _, _ = copy_case
    path = root / "data/claim_contract.json"
    data = json.loads(path.read_text())
    data["claims"][0][field] = value
    path.write_text(json.dumps(data))
    _failed(_validate(copy_case), "claim_evidence_ceilings")


def test_source_audit_controls_must_replay(copy_case):
    _, output, _ = copy_case
    path = output / "data/source_audit.json"
    data = json.loads(path.read_text())
    data["controls"]["snapshot_mutation_max"] = -1
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "source_reconstruction_scope")


@pytest.mark.parametrize("relative", ["data/analysis_protocol.json", "data/sampling_diagnostics.json"])
def test_analysis_and_sampling_records_reject_repaired_inventory_tampering(copy_case, relative):
    _, output, _ = copy_case
    path = output / relative
    data = json.loads(path.read_text())
    if relative.endswith("analysis_protocol.json"):
        data["alpha"] = 0.2
    else:
        data["cases"][0]["points"][0]["mean"] += 1
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))

    _failed(_validate(copy_case), "statistical_controls")


@pytest.mark.parametrize(
    ("filename", "gate"),
    [
        ("research_summary.md", "documentation_facts_replay"),
        ("documentation_audit.json", "documentation_closure"),
    ],
)
def test_documentation_receipts_reject_refreshed_forgeries(copy_case, filename, gate):
    _, output, _ = copy_case
    path = output / "reports" / filename
    if filename.endswith(".md"):
        path.write_text(path.read_text() + "\nAn invented quantity: 12345.\n")
    else:
        data = json.loads(path.read_text())
        data["local_links"] += 1
        path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), gate)


def test_exact_operating_probability_cannot_be_forged_after_inventory_refresh(copy_case):
    _, output, _ = copy_case
    path = output / "data/exact_decision.json"
    data = json.loads(path.read_text())
    data["operating_points"][0]["open_probability"] = 0.0
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "exact_decision_replay")


@pytest.mark.parametrize(
    ("filename", "gate"),
    [
        ("learning_parameters.json", "learned_parameters_replay"),
        ("gaze.json", "gaze_replication_and_extension_replay"),
    ],
)
def test_learned_parameters_and_gaze_replay_reject_refreshed_forgeries(copy_case, filename, gate):
    _, output, _ = copy_case
    path = output / "data" / filename
    data = json.loads(path.read_text())
    if filename == "learning_parameters.json":
        data[0]["pre"][0][0] += 0.01
        data[0]["pre"][1][0] -= 0.01
    else:
        data["transfer"][0]["positive_policy_change"] += 0.01
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), gate)


def test_requested_render_products_missing_return_false_not_exception(copy_case):
    root, output, models = copy_case
    report = validate_project(root, output, specification_dir=models)
    _failed(report, "rendered_products_present")
    _failed(report, "executed_notebook_present")


@pytest.mark.parametrize("target", ["critical", "interval", "coverage"])
def test_joint_replay_rejects_forged_results_after_checksum_refresh(copy_case, target):
    _, output, _ = copy_case
    path = output / "data/gaze_uncertainty.json"
    data = json.loads(path.read_text())
    if target == "critical":
        data["region"]["critical_value"] += 1
    elif target == "interval":
        data["region"]["intervals"][0]["low"] -= 0.1
    else:
        data["calibration"][0]["joint_coverage"]["count"] += 1
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "gaze_joint_uncertainty_replay")


def test_design_record_cannot_override_admitted_parameters(copy_case):
    _, output, _ = copy_case
    path = output / "data/study.json"
    data = json.loads(path.read_text())
    data["design"]["recall_precision"] += 1
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "gnn_main_model_binding")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("post_world_well", 1.2),
        ("entropy_post", 1.0),
        ("nll_post", -1.0),
        ("appreciation", 3.0),
        ("optimism_post", 3.0),
    ],
)
def test_independent_agent_numerical_bounds(copy_case, field, value):
    _, output, _ = copy_case
    path = output / "data/study.json"
    data = json.loads(path.read_text())
    row = next(row for row in data["rows"] if row["condition"] == "positive_recall")
    row[field] = value
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "paired_design")


def test_required_trace_counts_and_physical_font_metrics(copy_case):
    _, output, _ = copy_case
    path = output / "data/study.json"
    original = path.read_text()
    data = json.loads(original)
    data["traces"].pop()
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "paired_design")
    path.write_text(original)
    path = output / "reports/figure_source_map.json"
    figures = json.loads(path.read_text())
    figures[0]["publication_min_font_points"] = 100
    path.write_text(json.dumps(figures))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "figure_integrity_and_legibility")


def test_custody_rejects_changed_input_and_preserved_models_support_detached_validation(copy_case):
    root, output, models = copy_case
    assert validate_project(root, output, require_render=False).all_pass
    path = root / "docs/manuscript/manuscript.md"
    path.write_text(path.read_text() + "\nChanged research input.\n")
    _failed(_validate(copy_case), "research_input_custody")
    declaration = models / "gratitude.gnn.md"
    declaration.write_text(declaration.read_text() + "\n")
    _failed(_validate(copy_case), "preserved_specifications")


@pytest.mark.parametrize("invalid_manuscript", [False, True])
def test_replay_record_admission_precedence(copy_case, invalid_manuscript):
    _, output, _ = copy_case
    first = output / "data/emptiness_practice.json"
    first.write_text('{"schema":"missing-practice-fields"}')
    (output / "data/gaze.json").write_text("{invalid-gaze-json")
    if invalid_manuscript:
        (output / "reports/manuscript.md").write_bytes(b"\xff")
    with pytest.raises(ValidationError) as expected:
        read_record(first, PracticeAudit)
    report = _validate(copy_case)
    assert len(report.gates) == 1
    assert report.gates[0].name == "artifact_admission"
    assert report.gates[0].detail == str(expected.value)


def test_failed_gaze_control_short_circuits_invalid_replay_declaration(copy_case):
    _, output, _ = copy_case
    path = output / "data/gaze.json"
    data = json.loads(path.read_text())
    data["all_controls_pass"] = False
    path.write_text(json.dumps(data))
    (output / "specifications/gaze.gnn.md").write_text("Invalid declaration must not be consumed.")
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    report = _validate(copy_case)
    _failed(report, "gaze_replication_and_extension_replay")
    assert all(gate.name != "artifact_admission" for gate in report.gates)


def test_failed_boundary_control_short_circuits_its_invalid_declaration(copy_case):
    _, output, _ = copy_case
    path = output / "data/boundary_gaze.json"
    data = json.loads(path.read_text())
    data["all_controls_pass"] = False
    path.write_text(json.dumps(data))
    (output / "specifications/boundary_gaze.gnn.md").write_text("Invalid declaration must not execute.")
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "boundary_gaze_intersection_replay")


def test_forged_boundary_region_rejected_after_inventory_refresh(copy_case):
    _, output, _ = copy_case
    path = output / "data/boundary_gaze.json"
    data = json.loads(path.read_text())
    data["region"]["intervals"][0]["mean"] += 0.01
    path.write_text(json.dumps(data))
    write_record(output / "reports/artifact_manifest.json", inventory(output))
    _failed(_validate(copy_case), "boundary_gaze_intersection_replay")
