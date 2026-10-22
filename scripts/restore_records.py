# Copyright (c) 2026 Daniel Ari Friedman
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Restore the exact large records carried as gzip files in the public snapshot."""

from pathlib import Path

from pydantic import TypeAdapter

from thanks_for_nothing.retained_records import RetainedRecord, restore_records

if __name__ == "__main__":
    root = Path.cwd()
    inventory = root / "configs/retained-records.json"
    records = TypeAdapter(tuple[RetainedRecord, ...]).validate_json(inventory.read_text())
    restore_records(root / "output/data", records)
