# Copyright (c) 2026 Daniel Ari Friedman
from typing import TypedDict

class TensorValues(TypedDict):
    A: tuple[tuple[float, ...], ...]
    B: tuple[tuple[tuple[float, ...], ...], ...]
    C: tuple[float, ...]
    D: tuple[float, ...]

class RuntimeParameters(TypedDict):
    num_timesteps: int
    random_seed: int
    policy_len: int
    gamma: float
    alpha: float
    b_tensor_order: str

class CanonicalInput(TypedDict):
    model_name: str
    initialparameterization: TensorValues
    model_parameters: RuntimeParameters

def build_canonical_pomdp_spec(gnn_spec: CanonicalInput) -> CanonicalInput: ...
