# Copyright (c) 2026 Daniel Ari Friedman
from pathlib import Path
from typing import TypedDict

from gnn.render.pomdp_contract import CanonicalInput

class ExecutionResult(TypedDict, total=False):
    success: bool
    error: str
    reason: str

def run_pymdp_simulation(gnn_spec: CanonicalInput, output_dir: Path) -> tuple[bool, ExecutionResult]: ...
