# Copyright (c) 2026 Daniel Ari Friedman
"""Bind manuscript values to typed, serialized experiment records rather than prose literals."""

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import groupby
from math import gcd, lcm
from pathlib import Path

import numpy as np
from pydantic import BaseModel, JsonValue, TypeAdapter

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.contracts import ContractError, StudyDesign
from thanks_for_nothing.practice_inference import admitted_priors
from thanks_for_nothing.specifications import load_model
from thanks_for_nothing.visual_tokens import DISPLAY_SCALE


@dataclass(frozen=True, slots=True)
class ManuscriptVariable:
    """A rendered value with its exact producer bytes and an explicit source selector."""

    name: str
    value: str
    source_artifact: str
    source_sha256: str
    selector: str


def _display(value: JsonValue) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, list):
        return ", ".join(_display(item) for item in value)
    return str(value)


def _selection_rule(prior: tuple[Fraction, ...], support: tuple[bool, ...]) -> str:
    total = sum(prior, Fraction())
    opened = tuple(v / total for v in prior)
    retained = sum((v for v, active in zip(opened, support, strict=True) if active), Fraction())
    coefficients = tuple(
        v - (v / retained if active else Fraction()) for v, active in zip(opened, support, strict=True)
    )
    scale = lcm(*(v.denominator for v in coefficients))
    integers = tuple(int(v * scale) for v in coefficients)
    divisor = gcd(*integers)
    normalized = tuple(v // divisor for v in integers)
    sides = tuple(
        "+".join(
            (str(abs(v)) if abs(v) != 1 else "") + rf"L_{{{i + 1}}}(k)"
            for i, v in enumerate(normalized)
            if v * sign > 0
        )
        for sign in (1, -1)
    )
    return sides[0] + ">" + sides[1]


def _design_variables(
    prefix: str, design: BaseModel | StudyDesign, artifact: str, digest: str
) -> tuple[ManuscriptVariable, ...]:
    values = TypeAdapter(dict[str, JsonValue]).validate_json(record_json(design))
    return tuple(
        ManuscriptVariable(
            f"{prefix}_{name.upper()}", _display(value), artifact, digest, f"/design/{name}"
        )
        for name, value in values.items()
        if name not in {"conditions", "regimes"}
        and (
            isinstance(value, (str, int, float))
            or (isinstance(value, list) and all(isinstance(item, (str, int, float)) for item in value))
        )
    )


def manuscript_variables(bundle: ResearchBundle) -> tuple[ManuscriptVariable, ...]:
    """Generate values from the actual cohort, including reduced real-test designs."""
    study_hash = sha256(record_json(bundle.study).encode()).hexdigest()
    practice_hash = sha256(record_json(bundle.practice).encode()).hexdigest()
    gaze_hash = sha256(record_json(bundle.gaze).encode()).hexdigest()
    boundary_hash = sha256(record_json(bundle.boundary_gaze).encode()).hexdigest()
    joint_hash = sha256(record_json(bundle.gaze_uncertainty).encode()).hexdigest()
    provenance_hash = sha256(record_json(bundle.provenance).encode()).hexdigest()
    exact_hash = sha256(record_json(bundle.exact_decision).encode()).hexdigest()
    values = [
        *_design_variables("STUDY", bundle.study.design, "data/study.json", study_hash),
        *_design_variables(
            "PRACTICE", bundle.practice.design, "data/emptiness_practice.json", practice_hash
        ),
        *_design_variables("GAZE", bundle.gaze.design, "data/gaze.json", gaze_hash),
        *_design_variables(
            "BOUNDARY", bundle.boundary_gaze.design, "data/boundary_gaze.json", boundary_hash
        ),
        *_design_variables(
            "JOINT", bundle.gaze_uncertainty.design, "data/gaze_uncertainty.json", joint_hash
        ),
    ]
    for name, value, source, digest, selector in (
        (
            "AGENTS",
            len({row.paired_id for row in bundle.study.rows}),
            "data/study.json",
            study_hash,
            "count(unique(rows.paired_id))",
        ),
        (
            "REPLICATES",
            bundle.study.design.replicates,
            "data/study.json",
            study_hash,
            "/design/replicates",
        ),
        (
            "STUDY_STRATA",
            len(bundle.study.design.luckiness),
            "data/study.json",
            study_hash,
            "count(design.luckiness)",
        ),
        (
            "STUDY_CONDITIONS",
            len({row.condition for row in bundle.study.rows}),
            "data/study.json",
            study_hash,
            "count(unique(rows.condition))",
        ),
        (
            "PRIMARY_CONTRASTS",
            len(bundle.statistics.contrasts),
            "data/statistics.json",
            sha256(record_json(bundle.statistics).encode()).hexdigest(),
            "count(contrasts)",
        ),
        (
            "PRACTICE_CONDITIONS",
            len(bundle.practice.design.conditions),
            "data/emptiness_practice.json",
            practice_hash,
            "count(design.conditions)",
        ),
        (
            "PRACTICE_CONTEXTS",
            len(bundle.practice.design.contexts),
            "data/emptiness_practice.json",
            practice_hash,
            "count(design.contexts)",
        ),
        (
            "PRACTICE_WINDOWS",
            len(bundle.practice.design.contexts[0].probabilities),
            "data/emptiness_practice.json",
            practice_hash,
            "count(design.contexts[0].probabilities)",
        ),
        (
            "PRACTICE_CONTRASTS",
            len(bundle.practice.contrasts),
            "data/emptiness_practice.json",
            practice_hash,
            "count(contrasts)",
        ),
        (
            "GAZE_LOCATIONS",
            len(bundle.gaze.design.coordinates),
            "data/gaze.json",
            gaze_hash,
            "count(design.coordinates)",
        ),
        (
            "GAZE_CONDITIONS",
            len(bundle.gaze.design.conditions),
            "data/gaze.json",
            gaze_hash,
            "count(design.conditions)",
        ),
        ("GAZE_EPISODES", len(bundle.gaze.episodes), "data/gaze.json", gaze_hash, "count(episodes)"),
        (
            "GAZE_CONTEXTS",
            len(bundle.gaze.design.contexts),
            "data/gaze.json",
            gaze_hash,
            "count(design.contexts)",
        ),
        (
            "GAZE_REGION_POSITIVE",
            bundle.gaze.design.regions.count(0),
            "data/gaze.json",
            gaze_hash,
            "count(design.regions=0)",
        ),
        (
            "GAZE_REGION_NEGATIVE",
            bundle.gaze.design.regions.count(1),
            "data/gaze.json",
            gaze_hash,
            "count(design.regions=1)",
        ),
        (
            "GAZE_REGION_NEUTRAL",
            bundle.gaze.design.regions.count(2),
            "data/gaze.json",
            gaze_hash,
            "count(design.regions=2)",
        ),
        (
            "GAZE_WINDOWS",
            len(bundle.gaze.design.contexts[0].candidates),
            "data/gaze.json",
            gaze_hash,
            "count(design.contexts[0].candidates)",
        ),
        ("GAZE_CONTRASTS", len(bundle.gaze.contrasts), "data/gaze.json", gaze_hash, "count(contrasts)"),
        (
            "GAZE_TRANSFER_RECORDS",
            len(bundle.gaze.transfer),
            "data/gaze.json",
            gaze_hash,
            "count(transfer)",
        ),
        (
            "GAZE_TRANSFER_BRIDGES",
            len({r.bridge for r in bundle.gaze.transfer}),
            "data/gaze.json",
            gaze_hash,
            "count(unique(transfer.bridge))",
        ),
        (
            "GAZE_TRANSFER_COMPARISON_COUNT",
            len(bundle.gaze.design.transfer_comparisons),
            "data/gaze.json",
            gaze_hash,
            "count(design.transfer_comparisons)",
        ),
        (
            "GAZE_TRANSFER_ENDPOINT_COUNT",
            len({r.endpoint for r in bundle.gaze.contrasts if r.experiment == "transfer"}),
            "data/gaze.json",
            gaze_hash,
            "count(unique(contrasts[experiment=transfer].endpoint))",
        ),
        (
            "GAZE_ACTIVE_COMPARISON_COUNT",
            len(bundle.gaze.design.comparisons),
            "data/gaze.json",
            gaze_hash,
            "count(design.comparisons)",
        ),
        (
            "GAZE_ACTIVE_ENDPOINT_COUNT",
            len({r.endpoint for r in bundle.gaze.contrasts if r.experiment == "active"}),
            "data/gaze.json",
            gaze_hash,
            "count(unique(contrasts[experiment=active].endpoint))",
        ),
        (
            "GAZE_TRANSFER_UNIFORMS",
            bundle.gaze.design.transfer_steps - 1,
            "data/gaze.json",
            gaze_hash,
            "design.transfer_steps - initial location",
        ),
        (
            "GAZE_TRANSFER_CONTRASTS",
            sum(r.experiment == "transfer" for r in bundle.gaze.contrasts),
            "data/gaze.json",
            gaze_hash,
            "count(contrasts[experiment=transfer])",
        ),
        (
            "GAZE_ACTIVE_CONTRASTS",
            sum(r.experiment == "active" for r in bundle.gaze.contrasts),
            "data/gaze.json",
            gaze_hash,
            "count(contrasts[experiment=active])",
        ),
        (
            "BOUNDARY_UNITS",
            len({(r.regime, r.scene, r.boundary, r.replicate) for r in bundle.boundary_gaze.episodes}),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(unique(episodes.regime,scene,boundary,replicate))",
        ),
        (
            "BOUNDARY_EPISODES",
            len(bundle.boundary_gaze.episodes),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(episodes)",
        ),
        (
            "BOUNDARY_CONDITIONS",
            len(bundle.boundary_gaze.design.conditions),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.conditions)",
        ),
        (
            "BOUNDARY_CELLS",
            len({(r.regime, r.scene, r.boundary) for r in bundle.boundary_gaze.episodes}),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(unique(episodes.regime,scene,boundary))",
        ),
        (
            "BOUNDARY_SCENES",
            len(bundle.boundary_gaze.design.scene_maps),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.scene_maps)",
        ),
        (
            "BOUNDARY_STATES",
            len(bundle.boundary_gaze.design.scene_maps) ** 2,
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.scene_maps)^2",
        ),
        (
            "BOUNDARY_REGIMES",
            len(bundle.boundary_gaze.design.regimes),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.regimes)",
        ),
        (
            "BOUNDARY_PROBES",
            len(bundle.boundary_gaze.design.probe_reliabilities),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.probe_reliabilities)",
        ),
        (
            "BOUNDARY_CONTRASTS",
            len(bundle.boundary_gaze.region.intervals),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(region.intervals)",
        ),
        (
            "BOUNDARY_COMPARISONS",
            len(bundle.boundary_gaze.design.comparisons),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.comparisons)",
        ),
        (
            "BOUNDARY_VISUAL_COMPARISONS",
            sum(r[1] == "visual" for r in bundle.boundary_gaze.design.comparisons),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.comparisons[reference=visual])",
        ),
        (
            "BOUNDARY_ENDPOINT_COUNT",
            len(bundle.boundary_gaze.design.endpoints),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(design.endpoints)",
        ),
        (
            "BOUNDARY_EXACT",
            len(bundle.boundary_gaze.exact_offsets),
            "data/boundary_gaze.json",
            boundary_hash,
            "count(exact_offsets)",
        ),
        (
            "JOINT_CONFIDENCE_PERCENT",
            100 * bundle.gaze_uncertainty.design.confidence,
            "data/gaze_uncertainty.json",
            joint_hash,
            "100 * design.confidence",
        ),
        (
            "JOINT_BLOCKS",
            len(bundle.gaze_uncertainty.region.blocks),
            "data/gaze_uncertainty.json",
            joint_hash,
            "count(region.blocks)",
        ),
        (
            "JOINT_MC_PERCENT",
            100 * bundle.gaze_uncertainty.design.monte_carlo_confidence,
            "data/gaze_uncertainty.json",
            joint_hash,
            "100 * design.monte_carlo_confidence",
        ),
        (
            "POINTWISE_CONFIDENCE_PERCENT",
            100 * (1 - bundle.calibration.alpha),
            "data/statistical_calibration.json",
            sha256(record_json(bundle.calibration).encode()).hexdigest(),
            "100 * (1 - alpha); declared analysis confidence level",
        ),
        (
            "POINTWISE_ALPHA",
            bundle.calibration.alpha,
            "data/statistical_calibration.json",
            sha256(record_json(bundle.calibration).encode()).hexdigest(),
            "/alpha",
        ),
        (
            "POINTWISE_CONFIDENCE",
            1 - bundle.calibration.alpha,
            "data/statistical_calibration.json",
            sha256(record_json(bundle.calibration).encode()).hexdigest(),
            "1 - alpha",
        ),
        (
            "POINTWISE_LOWER",
            bundle.calibration.alpha / 2,
            "data/statistical_calibration.json",
            sha256(record_json(bundle.calibration).encode()).hexdigest(),
            "alpha / 2",
        ),
        (
            "POINTWISE_UPPER",
            1 - bundle.calibration.alpha / 2,
            "data/statistical_calibration.json",
            sha256(record_json(bundle.calibration).encode()).hexdigest(),
            "1 - alpha / 2",
        ),
        (
            "EXACT_RETAINED_MASS",
            bundle.exact_decision.restricted_prior_mass,
            "data/exact_decision.json",
            exact_hash,
            "/restricted_prior_mass",
        ),
        (
            "DISPLAY_SCALE",
            DISPLAY_SCALE,
            "data/statistics.json",
            sha256(record_json(bundle.statistics).encode()).hexdigest(),
            "display convention; estimates remain in native units",
        ),
    ):
        values.append(ManuscriptVariable(name, f"{value:g}", source, digest, selector))
    for dependency in bundle.provenance.dependencies:
        prefix = "RE" if dependency.distribution == "realizing-emptiness" else "GNN"
        for field, value in (("VERSION", dependency.version), ("COMMIT", dependency.commit)):
            values.append(
                ManuscriptVariable(
                    f"{prefix}_{field}",
                    value,
                    "data/provenance.json",
                    provenance_hash,
                    f"dependencies[distribution={dependency.distribution}].{field.lower()}",
                )
            )
    schedule = "; ".join(
        f"{probability:g} for {len(tuple(group))} windows"
        for probability, group in groupby(bundle.practice.design.contexts[-1].probabilities)
    )
    values.append(
        ManuscriptVariable(
            "PRACTICE_REVERSAL_SCHEDULE",
            schedule,
            "data/emptiness_practice.json",
            practice_hash,
            "/design/contexts[-1]/probabilities; run-length encoding",
        )
    )
    values.append(
        ManuscriptVariable(
            "PRACTICE_STATIONARY_PROBABILITY",
            f"{bundle.practice.design.contexts[0].probabilities[0]:g}",
            "data/emptiness_practice.json",
            practice_hash,
            "/design/contexts/0/probabilities/0",
        )
    )
    middle_reliability = bundle.boundary_gaze.design.probe_reliabilities[
        len(bundle.boundary_gaze.design.probe_reliabilities) // 2
    ]
    values.append(
        ManuscriptVariable(
            "BOUNDARY_MIDDLE_RELIABILITY",
            f"{middle_reliability:g}",
            "data/boundary_gaze.json",
            boundary_hash,
            "/design/probe_reliabilities[middle]",
        )
    )
    values.extend(
        ManuscriptVariable(
            f"GAZE_{context.name.upper()}_SEQUENCE",
            ",".join(str(c) for c in context.candidates),
            "data/gaze.json",
            gaze_hash,
            f"design.contexts[name={context.name}].candidates",
        )
        for context in bundle.gaze.design.contexts
    )
    return tuple(values)


def model_variables(bundle: ResearchBundle, specifications: Path) -> tuple[ManuscriptVariable, ...]:
    """Use the same admitted tensors and structural support as the executed experiment."""
    practice = load_model("emptiness_practice", specifications)
    gaze = load_model("gaze", specifications)
    if (
        practice.source_hash != bundle.practice.model_sha256
        or gaze.source_hash != bundle.gaze.model_sha256
    ):
        message = "Manuscript tensor declarations differ from the executed experiment"
        raise ContractError(message)
    restricted, open_prior = admitted_priors(practice, bundle.practice.design)
    raw = tuple(Fraction(str(v)) for v in practice.tensors.D)
    support = tuple(float(np.sum(restricted[i : i + 1])) > 0 for i in range(len(raw)))
    retained = sum(
        (v for i, v in enumerate(raw) if float(np.sum(restricted[i : i + 1])) > 0), Fraction()
    ) / sum(raw, Fraction())
    rows = (
        ("MODEL_PRACTICE_DEPLOYMENTS", str(len(bundle.practice.design.deployments)), practice),
        ("MODEL_PRACTICE_RESTRICTED_COUNT", str(sum(support)), practice),
        (
            "MODEL_PRACTICE_SCREEN_CHANNELS",
            str(len(bundle.practice.design.deployments[0].labels)),
            practice,
        ),
        ("MODEL_PRACTICE_CHANNEL_ZERO", ", ".join(f"{v:g}" for v in practice.tensors.A[0]), practice),
        (
            "MODEL_PRACTICE_RESTRICTED_PRIOR",
            ", ".join(
                f"{float(np.sum(restricted[index : index + 1])):g}" for index in range(len(restricted))
            ),
            practice,
        ),
        (
            "MODEL_PRACTICE_OPEN_PRIOR",
            ", ".join(
                f"{float(np.sum(open_prior[index : index + 1])):.6g}" for index in range(len(open_prior))
            ),
            practice,
        ),
        ("MODEL_GAZE_PREFERENCES", ",".join(f"{v:g}" for v in gaze.tensors.C), gaze),
        (
            "MODEL_PRACTICE_RETAINED_MASS_TEX",
            rf"\frac{{{retained.numerator}}}{{{retained.denominator}}}",
            practice,
        ),
        ("MODEL_PRACTICE_SELECTION_RULE_TEX", _selection_rule(raw, support), practice),
    )
    return tuple(
        ManuscriptVariable(
            name,
            value,
            f"specifications/{model.model_id}.gnn.md",
            model.source_hash,
            "admitted tensors / native admitted_priors",
        )
        for name, value, model in rows
    )


def parameter_table(variables: tuple[ManuscriptVariable, ...]) -> str:
    """Keep the changing protocol settings in a single automatically populated supplement."""
    rows = ["| Model / setting | Admitted value |", "| --- | --- |"]
    rows.extend(
        f"| {row.name.replace('_', ' ').lower()} | {row.value} |"
        for row in variables
        if row.selector.startswith("/design/") and not row.name.endswith(("CONDITIONS", "REGIMES"))
    )
    return "\n".join(rows)
