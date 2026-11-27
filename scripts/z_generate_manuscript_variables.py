# Copyright (c) 2026 Daniel Ari Friedman
# ruff: noqa: INP001
"""Invoke the retained Template reader without loading the model runtime."""

from pathlib import Path
from runpy import run_path

if __name__ == "__main__":
    reader = Path(__file__).resolve().parents[1] / "src/thanks_for_nothing/template_reader.py"
    _ = run_path(str(reader), run_name="__main__")
