# Copyright (c) 2026 Daniel Ari Friedman
from collections.abc import Sequence
from typing import TypeAlias

import numpy as np
from jax import Array
from numpy.typing import NDArray

NumericInput: TypeAlias = (
    NDArray[np.float64]
    | Sequence[float]
    | Sequence[Sequence[float]]
    | Sequence[Sequence[Sequence[float]]]
)

def asarray(a: NumericInput) -> Array: ...
def array(object: NumericInput) -> Array: ...  # noqa: A002 - Exact upstream keyword name.
