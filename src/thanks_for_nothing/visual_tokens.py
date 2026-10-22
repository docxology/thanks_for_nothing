# Copyright (c) 2026 Daniel Ari Friedman
"""Semantic condition labels and palette shared by every research surface."""

from typing import Final

DISPLAY_SCALE: Final = 1000

MAIN_RESULT_FIGURES: Final = frozenset(
    {"recall_situation", "practice_situation", "gaze_situation", "boundary_situation"}
)
SUPPLEMENT_ONLY_FIGURES: Final = frozenset(
    {
        "concept_operations",
        "boundary_task",
        "paired_contrasts",
        "practice_revision",
        "gaze_joint_uncertainty",
        "boundary_gaze_outcomes",
        "absence_information",
        "practice_policies",
        "yarbus_reconstruction",
        "task_settings",
    }
)

REQUIRED_FIGURES: Final = frozenset(
    {
        "gnn_model_graph",
        "gnn_model_tensors",
        "sampling_precision",
        "world_traditions",
        "concept_map",
        "concept_operations",
        "task_settings",
        "experiment_overview",
        "boundary_task",
        "learning_trajectories",
        "calibration_by_world",
        "paired_contrasts",
        "paired_spread",
        "weighting_sensitivity",
        "appreciation_null",
        "absence_information",
        "attention_policies",
        "sensitivity",
        "statistical_calibration",
        "practice_policies",
        "practice_revision",
        "exact_decision",
        "yarbus_reconstruction",
        "gaze_transfer_paths",
        "gaze_transfer_summary",
        "gaze_inquiry_paths",
        "gaze_inquiry_summary",
        "practice_mechanism",
        "gaze_joint_uncertainty",
        "joint_coverage",
        "boundary_information",
        "boundary_gaze_outcomes",
        "boundary_gaze_allocation",
        "boundary_gaze_convergence",
        "boundary_structure",
        "boundary_gaze_paths",
        *MAIN_RESULT_FIGURES,
    }
)

PALETTE: Final = {
    "no_recall": "#596579",
    "positive_recall": "#007C83",
    "matched_random_recall": "#B66A18",
    "absence_appreciation": "#8660A7",
    "ink": "#142E3A",
    "grid": "#E2E8EC",
    "harm": "#B74343",
    "artwork_overlay": "#FFFFFF",
}
LABELS: Final = {
    "no_recall": "No recall",
    "positive_recall": "Positive recall",
    "matched_random_recall": "Matched random recall",
    "absence_appreciation": "Absence valuation",
}

PRACTICE_LABELS: Final = {
    "rigid": "Rigid",
    "inquiry": "Inquiry",
    "no_preference": "No preference",
    "sham": "Sham",
    "no_access": "No access",
}
PRACTICE_ROLES: Final = {
    "rigid": "no_recall",
    "inquiry": "positive_recall",
    "no_preference": "matched_random_recall",
    "sham": "absence_appreciation",
    "no_access": "harm",
}

PROCESS_ROLES: Final = ("positive_recall", "matched_random_recall", "absence_appreciation", "harm")

GAZE_LABELS: Final = {
    "pragmatic_restricted": "Restricted utility",
    "pragmatic_open": "Open utility",
    "inquiry_open": "Open inquiry",
    "inquiry_restricted": "Restricted inquiry",
    "sham": "Sham",
    "uniform_open": "Uniform open",
}
GAZE_ROLES: Final = {
    "pragmatic_restricted": "no_recall",
    "pragmatic_open": "matched_random_recall",
    "inquiry_open": "positive_recall",
    "inquiry_restricted": "harm",
    "sham": "absence_appreciation",
    "uniform_open": "ink",
}

BOUNDARY_LABELS: Final = {
    "visual": "Visual only",
    "integrated": "Integrated",
    "boundary_only": "Boundary only",
    "uniform": "Uniform",
    "restricted": "Restricted",
    "sham": "Yoked sham",
}
BOUNDARY_ROLES: Final = {
    "visual": "no_recall",
    "integrated": "positive_recall",
    "boundary_only": "matched_random_recall",
    "uniform": "ink",
    "restricted": "harm",
    "sham": "absence_appreciation",
}
BOUNDARY_MARKERS: Final = {
    "visual": "o",
    "integrated": "o",
    "boundary_only": "s",
    "uniform": "^",
    "restricted": "D",
    "sham": "x",
}
