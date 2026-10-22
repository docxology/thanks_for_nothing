# Copyright (c) 2026 Daniel Ari Friedman
from typing import Protocol

import numpy as np

class _ScalarStudentT(Protocol):
    def ppf(self, q: float, df: float, *, loc: float = 0, scale: float = 1) -> np.float64: ...

t: _ScalarStudentT

class _ScalarBinomial(Protocol):
    def ppf(self, q: float, n: int, p: float) -> np.float64: ...
    def pmf(self, k: int, n: int, p: float) -> np.float64: ...

binom: _ScalarBinomial
