# Copyright (c) 2026 Daniel Ari Friedman
"""Composition checks on actual generated research records, including legal TeX."""

from dataclasses import replace

import pytest
from pydantic import TypeAdapter

from thanks_for_nothing.attention import AttentionAudit
from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.boundary_upstream import BoundaryUpstreamAudit
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.calibration import CalibrationAudit
from thanks_for_nothing.contracts import ContractError, StudyResult
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_joint import GazeUncertainty
from thanks_for_nothing.nothingness import NothingnessAudit
from thanks_for_nothing.practice_contracts import ExactDecisionAudit, PracticeAudit
from thanks_for_nothing.provenance import ProvenanceAudit
from thanks_for_nothing.reporting import compose_manuscript, hydration, main_findings
from thanks_for_nothing.sensitivity import SensitivityAudit
from thanks_for_nothing.source_reconstruction import SourceAudit
from thanks_for_nothing.statistics import StatisticalReport
from thanks_for_nothing.upstream_practice import UpstreamPracticeAudit
from thanks_for_nothing.validation import read_record


@pytest.fixture
def research_bundle(pipeline_case):
    data = pipeline_case.output / "data"
    return ResearchBundle(
        read_record(data / "provenance.json", ProvenanceAudit),
        TypeAdapter(SourceAudit).validate_json((data / "source_audit.json").read_text()),
        read_record(data / "study.json", StudyResult),
        read_record(data / "statistics.json", StatisticalReport),
        read_record(data / "nothingness.json", NothingnessAudit),
        read_record(data / "attention.json", AttentionAudit),
        read_record(data / "statistical_calibration.json", CalibrationAudit),
        read_record(data / "sensitivity.json", SensitivityAudit),
        read_record(data / "emptiness_practice.json", PracticeAudit),
        read_record(data / "upstream_practice.json", UpstreamPracticeAudit),
        read_record(data / "exact_decision.json", ExactDecisionAudit),
        read_record(data / "gaze.json", GazeAudit),
        read_record(data / "gaze_uncertainty.json", GazeUncertainty),
        read_record(data / "boundary_gaze.json", BoundaryGazeAudit),
        read_record(data / "boundary_upstream.json", BoundaryUpstreamAudit),
    )


def test_hydration_preserves_legal_nested_tex_and_rejects_unknown_token(research_bundle, tmp_path):
    manuscript = tmp_path / "docs/manuscript/manuscript.md"
    manuscript.parent.mkdir(parents=True)
    tex = (
        r"$q_{\mathrm{post}}$ with {{AGENTS}} agents."
        "\n\n![A source-bound figure.](output/figures/test.png){#fig-test width=100%}"
    )
    manuscript.write_text(tex)
    output = tmp_path / "artifacts"
    composed = compose_manuscript(tmp_path, output, research_bundle).read_text()
    assert r"$q_{\mathrm{post}}$" in composed
    assert "2 agents" in composed
    assert "artifacts/figures/test.png" in composed
    manuscript.write_text(tex + "\n{{UNKNOWN_VARIABLE}}")
    with pytest.raises(ContractError, match="Unresolved manuscript variable"):
        compose_manuscript(tmp_path, output, research_bundle)


def test_findings_are_complete_and_empty_grid_rejected(research_bundle):
    text = main_findings(research_bundle)
    rows = [
        line
        for line in text.splitlines()
        if line.startswith("| ") and not line.startswith(("| Contrast", "| ---"))
    ]
    estimates = [float(line.split("|")[2]) for line in rows]
    expected = [1000 * row.estimate.mean_difference for row in research_bundle.statistics.contrasts]
    assert estimates == pytest.approx(expected, abs=0.0005)
    replacements = hydration(research_bundle)
    assert len({item.token for item in replacements}) == len(replacements)
    assert "{{EXPERIMENT_LOGIC_TABLE}}" in {item.token for item in replacements}
    assert all(item.text for item in replacements)
    empty = replace(research_bundle, sensitivity=replace(research_bundle.sensitivity, rows=()))
    with pytest.raises(ContractError, match="at least one"):
        hydration(empty)
