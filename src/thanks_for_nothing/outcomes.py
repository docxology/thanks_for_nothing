# Copyright (c) 2026 Daniel Ari Friedman
"""Declared changes in distinct predictive and task outcomes."""

from typing import Literal, assert_never

from thanks_for_nothing.contracts import AgentResult

Endpoint = Literal["optimism_change", "brier_change", "nll_change"]


def endpoint_change(row: AgentResult, endpoint: Endpoint) -> float:
    """Keep outcome directions explicit: Brier and log loss are losses."""
    match endpoint:
        case "optimism_change":
            return row.optimism_post - row.optimism_pre
        case "brier_change":
            return row.brier_post - row.brier_pre
        case "nll_change":
            return row.nll_post - row.nll_pre
        case _:
            assert_never(endpoint)
