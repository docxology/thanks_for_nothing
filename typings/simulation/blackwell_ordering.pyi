# Copyright (c) 2026 Daniel Ari Friedman
from typing import TypedDict

class BlackwellResult(TypedDict):
    original_bayes_risk: float
    chance_risk: float
    all_controls_pass: bool

def build_blackwell_bayes_risk_audit(*, grid_steps: int | None = None) -> BlackwellResult: ...
