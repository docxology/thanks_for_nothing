# Copyright (c) 2026 Daniel Ari Friedman
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Explicitly fetch omitted inputs from their original hosts for local research."""

import argparse
from pathlib import Path

from rich.console import Console

from thanks_for_nothing.external_inputs import acquire_external_inputs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()
    root = arguments.root.resolve()
    for path in acquire_external_inputs(root, root / "configs/external-inputs.json"):
        Console().print(str(path.relative_to(root)))
