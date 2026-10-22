# Copyright (c) 2026 Daniel Ari Friedman
from typing import Literal, overload

from jax import Array

class Agent:
    def __init__(
        self,
        *,
        A: list[Array],  # noqa: N803 - Exact upstream tensor keyword.
        B: list[Array],  # noqa: N803 - Exact upstream tensor keyword.
        C: list[Array],  # noqa: N803 - Exact upstream tensor keyword.
        D: list[Array],  # noqa: N803 - Exact upstream tensor keyword.
        num_controls: list[int],
        control_fac_idx: list[int],
        policy_len: int,
        gamma: float,
        alpha: float,
        batch_size: int,
    ) -> None: ...
    @overload
    def infer_states(
        self, observations: list[Array], *, empirical_prior: list[Array], return_info: Literal[True]
    ) -> tuple[list[Array], dict[str, Array]]: ...
    @overload
    def infer_states(
        self,
        observations: list[Array],
        *,
        empirical_prior: list[Array],
        return_info: Literal[False] = False,
    ) -> list[Array]: ...
    def infer_policies(self, qs: list[Array]) -> tuple[Array, Array]: ...
    def update_empirical_prior(self, action: Array, qs: list[Array]) -> list[Array]: ...
