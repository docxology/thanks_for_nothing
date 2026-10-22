# Copyright (c) 2026 Daniel Ari Friedman
"""Validate artifact identity, paired designs and bounded scientific language."""

import re
from math import isfinite, log
from pathlib import Path

import numpy as np

from thanks_for_nothing.artifact_checks import read_record
from thanks_for_nothing.attention import AttentionAudit
from thanks_for_nothing.contracts import Condition, ContractError, StudyResult
from thanks_for_nothing.custody import SourceTreeReceipt, source_tree_receipt


def _numerical_bounds(study: StudyResult) -> bool:
    """Apply independent probability, loss and valuation bounds to every agent."""
    for row in study.rows:
        probabilities = (row.pre_world_well, row.post_world_well, row.brier_pre, row.brier_post)
        if not all(isfinite(value) and 0 <= value <= 1 for value in probabilities):
            return False
        bounds = (
            (row.entropy_post, 0.0, log(2.0)),
            (row.nll_pre, 0.0, float("inf")),
            (row.nll_post, 0.0, float("inf")),
            (row.appreciation, 0.0, study.design.reference_hazard * study.design.harm_cost),
            (row.mean_recall_count, 0.0, float(study.design.recall_count)),
            (row.optimism_pre, -2.0, 2.0),
            (row.optimism_post, -2.0, 2.0),
        )
        if not all(isfinite(value) and low <= value <= high for value, low, high in bounds):
            return False
        if re.fullmatch(r"[0-9a-f]{64}", row.exposure_sha256) is None:
            return False
    return True


def _traces_valid(study: StudyResult) -> bool:
    """Require every independent unit's trajectory at all declared day indices."""
    expected = {
        (luck, condition, replicate, day)
        for luck in study.design.luckiness
        for condition in Condition
        for replicate in range(study.design.replicates)
        for day in range(1, study.design.baseline_days + study.design.intervention_days + 1)
    }
    observed = {(row.luckiness, row.condition, row.replicate, row.day) for row in study.traces}
    return (
        expected == observed
        and len(observed) == len(study.traces)
        and all(isfinite(row.world_well) and 0 <= row.world_well <= 1 for row in study.traces)
    )


def source_tree_valid(root: Path, output: Path) -> bool:
    """Compare live research input identity with its original execution receipt."""
    try:
        current = source_tree_receipt(root)
    except ContractError:
        return False
    return current == read_record(output / "data/source_tree.json", SourceTreeReceipt)


def paired_design(study: StudyResult) -> bool:
    """Check balanced exposures, matched doses and independent numerical bounds."""
    expected = {
        (luck, rep, condition)
        for luck in study.design.luckiness
        for rep in range(study.design.replicates)
        for condition in Condition
    }
    observed = {(row.luckiness, row.replicate, row.condition) for row in study.rows}
    if observed != expected or len(observed) != len(study.rows):
        return False
    for stratum, luck in enumerate(study.design.luckiness):
        for rep in range(study.design.replicates):
            rows = [row for row in study.rows if row.luckiness == luck and row.replicate == rep]
            if any(row.paired_id != f"{stratum}:{rep}" for row in rows):
                return False
            if (
                len(
                    {
                        (
                            row.exposure_sha256,
                            row.paired_id,
                            row.pre_world_well,
                            row.brier_pre,
                            row.nll_pre,
                            row.optimism_pre,
                        )
                        for row in rows
                    }
                )
                != 1
            ):
                return False
            absence = next(row for row in rows if row.condition == Condition.ABSENCE)
            baseline = next(row for row in rows if row.condition == Condition.NO_RECALL)
            if (absence.post_world_well, absence.brier_post, absence.optimism_post) != (
                baseline.post_world_well,
                baseline.brier_post,
                baseline.optimism_post,
            ):
                return False
            positive = next(row for row in rows if row.condition == Condition.POSITIVE)
            random = next(row for row in rows if row.condition == Condition.RANDOM)
            if positive.mean_recall_count != random.mean_recall_count:
                return False
    values = np.array(
        [
            (
                row.pre_world_well,
                row.post_world_well,
                row.brier_pre,
                row.brier_post,
                row.nll_pre,
                row.nll_post,
                row.optimism_pre,
                row.optimism_post,
                row.appreciation,
            )
            for row in study.rows
        ]
    )
    return bool(
        np.isfinite(values).all()
        and all(study.controls.values())
        and _numerical_bounds(study)
        and _traces_valid(study)
    )


def attention_valid(audit: AttentionAudit) -> bool:
    """Verify finite normalized native attention probabilities and controls."""
    for receipt in (*audit.native_receipts, *audit.rows):
        policies = np.asarray(receipt.policy_posterior, dtype=np.float64)
        beliefs = np.asarray(receipt.beliefs, dtype=np.float64)
        if (
            not np.isfinite(policies).all()
            or not np.isfinite(beliefs).all()
            or (policies < 0).any()
            or (beliefs < 0).any()
            or (abs(np.sum(policies, axis=1, dtype=np.float64) - 1) > 1e-6 + 1e-5).any()
            or (abs(np.sum(beliefs, axis=1, dtype=np.float64) - 1) > 1e-6 + 1e-5).any()
        ):
            return False
    for row in audit.rows:
        if abs(row.positive_mass + row.negative_mass + row.neutral_mass - 1) > 1e-8 + 1e-5:
            return False
    return all(audit.controls.values()) and audit.all_controls_pass
