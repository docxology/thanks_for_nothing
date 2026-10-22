# Copyright (c) 2026 Daniel Ari Friedman
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Run in the synced project: uv run python scripts/run_pipeline.py
"""Run the project CLI through the synchronized project environment."""

import sys

from thanks_for_nothing.cli import app

if __name__ == "__main__":
    app(["run", *sys.argv[1:]])
