# Copyright (c) 2026 Daniel Ari Friedman
"""One exploratory gaze family, with explicit independent blocks and executable exact identities."""

from dataclasses import dataclass, replace
from hashlib import sha256
from typing import Final

import numpy as np

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_contracts import GazeAudit
from thanks_for_nothing.gaze_samples import GazeSample, active_samples, transfer_samples
from thanks_for_nothing.joint_calibration import JointCalibration, calibrate_joint_regions
from thanks_for_nothing.joint_contracts import JointBlock, JointDesign, JointRegion
from thanks_for_nothing.simultaneous import joint_region

ESTIMATE_REPLAY_TOLERANCE: Final = 1e-12


@dataclass(frozen=True, slots=True)
class GazeUncertainty:
    """Source-bound joint region plus independently known-answer operating characteristics."""

    schema: str
    gaze_sha256: str
    design: JointDesign
    region: JointRegion
    calibration: tuple[JointCalibration, ...]
    controls: dict[str, bool]
    all_controls_pass: bool


def _exact_identities(audit: GazeAudit) -> None:
    transfer = {(r.bridge, r.paired_id, r.condition): r for r in audit.transfer}
    episodes = {(r.context, r.replicate, r.window, r.condition): r for r in audit.episodes}
    if any(
        replace(row, condition="no_recall") != transfer[row.bridge, row.paired_id, "no_recall"]
        for row in audit.transfer
        if row.condition == "absence_appreciation"
    ) or any(
        replace(row, condition="pragmatic_restricted")
        != episodes[row.context, row.replicate, row.window, "pragmatic_restricted"]
        for row in audit.episodes
        if row.condition == "sham"
    ):
        message = "Mechanism-exact valuation/sham identity is violated in the supplied gaze records"
        raise ContractError(message)


def _block(name: str, samples: tuple[GazeSample, ...]) -> JointBlock:
    return JointBlock(
        name,
        tuple("/".join(row.identity) for row in samples),
        np.asarray([row.values for row in samples], dtype=np.float64).transpose((1, 2, 0)),
        tuple(
            row.identity[2:4]
            in (("absence_appreciation", "no_recall"), ("sham", "pragmatic_restricted"))
            for row in samples
        ),
    )


def build_gaze_uncertainty(audit: GazeAudit) -> GazeUncertainty:
    """Share complete vectors within blocks and keep active contexts independent.

    Exact-zero licenses are granted by named executable intervention identities,
    not by observing zero sample variance. Other sample constants stay unavailable.
    """
    transfer = transfer_samples(audit.transfer, audit.design)
    active = active_samples(audit.episodes, audit.design)
    _exact_identities(audit)
    blocks = (
        _block("transfer", transfer),
        *(
            _block(context.name, tuple(row for row in active if row.identity[1] == context.name))
            for context in audit.design.contexts
        ),
    )
    region = joint_region(blocks, audit.design.joint)
    original = {
        f"{r.experiment}/{r.context}/{r.condition}/{r.reference}/{r.endpoint}": r.intervals
        for r in audit.contrasts
    }
    if len(original) != len(audit.contrasts) or set(original) != {r.key for r in region.intervals}:
        message = "Joint contrast identities differ from the complete pointwise source family"
        raise ContractError(message)
    controls = {
        "contrast_identity_closure": {r.key for r in region.intervals} == set(original),
        "point_estimates_preserved": all(
            abs(row.mean - original[row.key].mean) < ESTIMATE_REPLAY_TOLERANCE
            for row in region.intervals
        ),
        "original_standard_errors_preserved": all(
            abs(row.standard_error - original[row.key].standard_error) < ESTIMATE_REPLAY_TOLERANCE
            for row in region.intervals
        ),
        "mechanism_identities_checked": True,
    }
    return GazeUncertainty(
        "thanks_for_nothing.gaze_uncertainty.v1",
        sha256(record_json(audit).encode()).hexdigest(),
        audit.design.joint,
        region,
        calibrate_joint_regions(
            audit.design.joint, rate_confidence=audit.contrasts[0].intervals.confidence
        ),
        controls,
        all(controls.values()),
    )
