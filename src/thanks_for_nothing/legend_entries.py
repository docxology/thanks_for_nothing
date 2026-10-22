# Copyright (c) 2026 Daniel Ari Friedman
"""Figure-specific meanings that are not already declared by labeled plot artists."""

from dataclasses import dataclass
from typing import Final, Literal

from thanks_for_nothing.concepts import CONCEPTS


@dataclass(frozen=True, slots=True)
class KeyGlyph:
    """A labeled visual encoding in the shared semantic palette."""

    label: str
    role: str = "ink"
    marker: str = ""
    linestyle: Literal["-", "--", ":", "-.", "None"] = "-"
    kind: Literal["line", "band", "text"] = "line"
    outline: bool = False


_CONCEPT_KEYS: Final = tuple(KeyGlyph(c.label, c.role, "s", "None") for c in CONCEPTS)
_PATH_KEYS: Final = (
    KeyGlyph("Line: sampled scene sequence", "artwork_overlay", outline=True),
    KeyGlyph("Circle: first displayed site", "artwork_overlay", "o", "None", outline=True),
    KeyGlyph("Square: last displayed site", "artwork_overlay", "s", "None", outline=True),
)
_INTERVAL_KEYS: Final = (
    KeyGlyph("Circle: stochastic estimate", marker="o", linestyle="None"),
    KeyGlyph("Square: mechanism-exact value", marker="s", linestyle="None"),
    KeyGlyph("Cross: interval unavailable", marker="x", linestyle="None"),
    KeyGlyph("Whiskers: joint bootstrap bounds"),
)

EXTRA_KEYS: Final = {
    "gnn_model_graph": (
        KeyGlyph("Circle: parsed GNN variable", "positive_recall", "o", "None"),
        KeyGlyph("Arrow: declared dependency", marker=">"),
        KeyGlyph("s state; o observation; u action", kind="text"),
    ),
    "gnn_model_tensors": (
        KeyGlyph("Dimensions: admitted tensor shapes", kind="text"),
        KeyGlyph("Rows: complete runtime families", kind="text"),
        KeyGlyph("R: restricted prior support", kind="text"),
    ),
    "world_traditions": (
        KeyGlyph("Rows: selected textual witnesses", kind="text"),
        KeyGlyph("Columns: questions, not measured quantities", kind="text"),
    ),
    "experiment_overview": (
        KeyGlyph("Manipulation / matched input", "no_recall", "s", "None"),
        KeyGlyph("Independent assessment", "positive_recall", "s", "None"),
        KeyGlyph("Control or evidential limit", "harm", "s", "None"),
    ),
    "concept_map": (
        *_CONCEPT_KEYS,
        KeyGlyph("Arrows: declared operations", marker=">"),
        KeyGlyph("Symbols: s state, q belief, o observation", kind="text"),
    ),
    "concept_operations": (*_CONCEPT_KEYS, KeyGlyph("Arrows: computational sequence", marker=">")),
    "task_settings": (
        KeyGlyph("Circle: positive scene site", "positive_recall", "o", "None"),
        KeyGlyph("Triangle: negative scene site", "harm", "v", "None"),
        KeyGlyph("Square: neutral scene site", "no_recall", "s", "None"),
        KeyGlyph("Arrow: model dependency", marker=">"),
    ),
    "boundary_task": (
        KeyGlyph("Scene and spatial observations", "positive_recall", "s", "None"),
        KeyGlyph("Encoding and structural questions", "absence_appreciation", "s", "None"),
        KeyGlyph("Arrows: declared dependencies", marker=">"),
    ),
    "learning_trajectories": (
        KeyGlyph("Vertical line: replay begins", "grid"),
        KeyGlyph("Shading: between-agent IQR", "no_recall", kind="band"),
    ),
    "calibration_by_world": (KeyGlyph("Shading: between-unit IQR", "no_recall", kind="band"),),
    "paired_contrasts": (KeyGlyph("Zero line: equal paired change"),),
    "paired_spread": (KeyGlyph("Segments: unit IQR; not a CI"),),
    "weighting_sensitivity": (KeyGlyph("Ranges: mixtures; not CIs", kind="text"),),
    "appreciation_null": (
        KeyGlyph("Line: counterfactual value mean", "absence_appreciation", "o"),
        KeyGlyph("Shading: between-unit IQR", "absence_appreciation", kind="band"),
        KeyGlyph("Right: exact paired maxima", kind="text"),
    ),
    "absence_information": (
        KeyGlyph("Prior / B: missing observation", "no_recall", "s", "None"),
        KeyGlyph("A: observed absence", "positive_recall", "s", "None"),
    ),
    "attention_policies": (KeyGlyph("Connector: profile comparison", "grid"),),
    "sensitivity": (KeyGlyph("Color bars: signed contrast", kind="text"),),
    "statistical_calibration": (KeyGlyph("Whiskers: exact binomial interval"),),
    "sampling_precision": (KeyGlyph("Prefixes share earlier units", kind="text"),),
    "practice_policies": (KeyGlyph("Bars: descriptive window means", kind="text"),),
    "practice_revision": (
        KeyGlyph("Circle: stationary context", marker="o", linestyle="None"),
        KeyGlyph("Square: reversal context", marker="s", linestyle="None"),
        KeyGlyph("Whiskers: pointwise analytic interval"),
    ),
    "practice_mechanism": (
        KeyGlyph("Solid: implemented dependency", "positive_recall", marker=">"),
        KeyGlyph("Dashed: unmeasured proposal", "no_recall", linestyle="--", marker=">"),
    ),
    "exact_decision": (KeyGlyph("Zero: equal model evidence"),),
    "yarbus_reconstruction": (
        *_PATH_KEYS,
        KeyGlyph("Source positive profile", "positive_recall", "s", "None"),
        KeyGlyph("Source negative profile", "harm", "s", "None"),
    ),
    "gaze_transfer_paths": _PATH_KEYS,
    "gaze_transfer_summary": (KeyGlyph("Whiskers: pointwise analytic interval"),),
    "gaze_inquiry_paths": _PATH_KEYS,
    "gaze_inquiry_summary": (
        KeyGlyph("Circle: stationary context", marker="o", linestyle="None"),
        KeyGlyph("Square: reversal context", marker="s", linestyle="None"),
        KeyGlyph("Whiskers: pointwise analytic interval"),
        KeyGlyph("Colors: named policies in rows", kind="text"),
    ),
    "gaze_joint_uncertainty": (
        KeyGlyph("Mechanism-exact value", "absence_appreciation", "s", "None"),
        KeyGlyph("Unavailable interval", "harm", "x", "None"),
    ),
    "joint_coverage": (
        KeyGlyph("Complete-region availability", "absence_appreciation", "s", "None"),
        KeyGlyph("Whiskers: exact binomial interval"),
        KeyGlyph("Vertical line: nominal coverage"),
    ),
    "boundary_information": (KeyGlyph("Shared color scale: conditional probability", kind="text"),),
    "boundary_gaze_outcomes": (*_INTERVAL_KEYS, KeyGlyph("Colors: named policies in rows", kind="text")),
    "boundary_gaze_allocation": (
        KeyGlyph("Points: descriptive means", kind="text"),
        KeyGlyph("Segments: pooled-unit IQR; not CIs"),
    ),
    "boundary_gaze_convergence": (KeyGlyph("Prefixes share earlier units", kind="text"),),
    "boundary_structure": (KeyGlyph("Color bars: signed matrix values", kind="text"),),
    "boundary_gaze_paths": (
        *_PATH_KEYS,
        KeyGlyph("Visual-only decisions", "no_recall", "o", "None"),
        KeyGlyph("Integrated decisions", "positive_recall", "o", "None"),
    ),
    "recall_situation": (
        KeyGlyph("Arrows: declared learning / replay", marker=">"),
        KeyGlyph("Whiskers: pointwise analytic interval"),
    ),
    "practice_situation": (
        KeyGlyph("Arrow: implemented sequence", marker=">"),
        KeyGlyph("Whiskers: pointwise analytic interval"),
    ),
    "gaze_situation": (
        KeyGlyph("Circle / triangle / square: positive / negative / neutral sites", kind="text"),
        KeyGlyph("Dashed: alternative transfer bridge", linestyle="--"),
    ),
    "boundary_situation": (*_INTERVAL_KEYS, KeyGlyph("Arrows: scene / encoding queries", marker=">")),
}
