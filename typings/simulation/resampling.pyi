# Copyright (c) 2026 Daniel Ari Friedman
from typing_extensions import TypedDict

class BinomialSummary(TypedDict):
    hits: int
    trials: int
    rate: float
    mcse: float
    confidence_level: float
    ci_low: float
    ci_high: float

def binomial_summary(hits: int, trials: int, *, confidence: float = 0.95) -> BinomialSummary: ...
