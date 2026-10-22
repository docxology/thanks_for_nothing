# Copyright (c) 2026 Daniel Ari Friedman
"""Complete paired contrast vectors; windows and locations never become independent units."""

from dataclasses import dataclass
from itertools import product
from typing import Literal, assert_never

import numpy as np
from numpy.typing import NDArray

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_contracts import GazeDesign, GazeEpisode, TransferGaze
from thanks_for_nothing.joint_contracts import MIN_PAIRED_UNITS

GazeKey = tuple[Literal["transfer", "active"], str, str, str, str]
TransferEndpoint = Literal["positive_policy_change", "balanced_loss_change"]
ActiveEndpoint = Literal["mean_balanced_log_loss", "positive_occupancy", "mean_movement_cost"]


@dataclass(frozen=True, slots=True)
class GazeSample:
    """A single contrast's fixed-stratum by independent-paired-unit differences."""

    identity: GazeKey
    values: NDArray[np.float64]


def _transfer_value(row: TransferGaze, endpoint: TransferEndpoint) -> float:
    match endpoint:
        case "positive_policy_change":
            return row.positive_policy_change
        case "balanced_loss_change":
            return row.balanced_loss_change
        case _:
            assert_never(endpoint)


def _active_value(row: GazeEpisode, endpoint: ActiveEndpoint) -> float:
    match endpoint:
        case "mean_balanced_log_loss":
            return row.mean_balanced_log_loss
        case "positive_occupancy":
            return row.positive_occupancy
        case "mean_movement_cost":
            return row.mean_movement_cost
        case _:
            assert_never(endpoint)


def transfer_samples(rows: tuple[TransferGaze, ...], design: GazeDesign) -> tuple[GazeSample, ...]:
    """Admit balanced identities and exposures before assembling all bridge columns."""
    index = {(row.bridge, row.condition, row.luckiness, row.replicate): row for row in rows}
    strata = sorted({row.luckiness for row in rows})
    replicates = sorted({row.replicate for row in rows})
    bridges = sorted({row.bridge for row in rows})
    conditions = {name for comparison in design.transfer_comparisons for name in comparison}
    if (
        not rows
        or len(replicates) < MIN_PAIRED_UNITS
        or len(index) != len(rows)
        or set(index) != set(product(bridges, conditions, strata, replicates))
    ):
        message = "Transfer uncertainty requires complete unique paired agent vectors"
        raise ContractError(message)
    for stratum, replicate in product(strata, replicates):
        paired = [
            index[bridge, condition, stratum, replicate]
            for bridge, condition in product(bridges, conditions)
        ]
        if (
            len({row.paired_id for row in paired}) != 1
            or len({row.exposure_sha256 for row in paired}) != 1
        ):
            message = "Transfer uncertainty requires matched paired identities and exposures"
            raise ContractError(message)
    samples: list[GazeSample] = []
    for bridge in bridges:
        for condition, reference in design.transfer_comparisons:
            for endpoint in ("positive_policy_change", "balanced_loss_change"):
                values = np.asarray(
                    [
                        [
                            _transfer_value(index[bridge, condition, stratum, rep], endpoint)
                            - _transfer_value(index[bridge, reference, stratum, rep], endpoint)
                            for rep in replicates
                        ]
                        for stratum in strata
                    ],
                    dtype=np.float64,
                )
                samples.append(GazeSample(("transfer", bridge, condition, reference, endpoint), values))
    return tuple(samples)


def active_samples(rows: tuple[GazeEpisode, ...], design: GazeDesign) -> tuple[GazeSample, ...]:
    """Average paired windows first; independent contexts remain separate blocks."""
    index = {(row.context, row.condition, row.replicate, row.window): row for row in rows}
    expected = {
        (context.name, condition, replicate, window)
        for context in design.contexts
        for condition, replicate, window in product(
            design.conditions, range(design.replicates), range(len(context.candidates))
        )
    }
    if len(index) != len(rows) or set(index) != expected:
        message = "Active uncertainty requires complete unique paired replicate/window vectors"
        raise ContractError(message)
    for context in design.contexts:
        for replicate, window in product(range(design.replicates), range(len(context.candidates))):
            paired = [
                index[context.name, condition, replicate, window] for condition in design.conditions
            ]
            if len({row.exposure_sha256 for row in paired}) != 1 or any(
                row.true_candidate != context.candidates[window] for row in paired
            ):
                message = "Active uncertainty requires matched potential outcomes and candidates"
                raise ContractError(message)
    samples: list[GazeSample] = []
    for context in design.contexts:
        for condition, reference in design.comparisons:
            for endpoint in ("mean_balanced_log_loss", "positive_occupancy", "mean_movement_cost"):
                values = np.asarray(
                    [
                        [
                            np.mean(
                                [
                                    _active_value(index[context.name, condition, rep, window], endpoint)
                                    - _active_value(
                                        index[context.name, reference, rep, window], endpoint
                                    )
                                    for window in range(len(context.candidates))
                                ]
                            )
                            for rep in range(design.replicates)
                        ]
                    ],
                    dtype=np.float64,
                )
                samples.append(
                    GazeSample(("active", context.name, condition, reference, endpoint), values)
                )
    return tuple(samples)
