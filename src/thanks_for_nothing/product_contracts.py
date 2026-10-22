# Copyright (c) 2026 Daniel Ari Friedman
"""Required scientific products and explicit finite-model scope."""

from typing import Final, Literal

NotebookName = Literal["gratitude_absence", "belief_updating", "gaze_emptiness", "boundary_gaze"]
NOTEBOOK_NAMES: Final[tuple[NotebookName, ...]] = (
    "gratitude_absence",
    "belief_updating",
    "gaze_emptiness",
    "boundary_gaze",
)
MIN_RENDER_BYTES: Final = 1000
EVIDENCE_CEILING: Final = "Finite model validation; no empirical efficacy, attainment or neural claim."
REQUIRED_SPECIFICATION_NAMES: Final = (
    "analysis",
    "gratitude",
    "nothingness",
    "attention_positive",
    "attention_negative",
    "emptiness_practice",
    "gaze",
    "boundary_gaze",
)
FORBIDDEN_MANUSCRIPT_PHRASES: Final = (
    "demonstrates that gratitude improves",
    "proves enlightenment",
    "clinically effective treatment",
)
REQUIRED_OUTPUTS: Final = (
    "data/gnn_graphs.json",
    "data/generative_models.json",
    "data/world_traditions.json",
    "world_traditions.html",
    "data/analysis_protocol.json",
    "data/sampling_diagnostics.json",
    "data/source_tree.json",
    "data/source_audit.json",
    "data/study.json",
    "data/statistics.json",
    "data/nothingness.json",
    "data/attention.json",
    "data/statistical_calibration.json",
    "data/sensitivity.json",
    "data/emptiness_practice.json",
    "data/upstream_practice.json",
    "data/exact_decision.json",
    "data/gaze.json",
    "data/gaze_uncertainty.json",
    "data/boundary_gaze.json",
    "data/boundary_upstream.json",
    "data/learning_parameters.json",
    "reports/formalisms.json",
    "reports/illustrations.json",
    "reports/documentation_audit.json",
    "reports/research_summary.md",
    "reports/manuscript.md",
    "reports/manuscript_variables.json",
    "reports/figure_source_map.json",
    "reports/artifact_manifest.json",
)
