# Copyright (c) 2026 Daniel Ari Friedman
from pathlib import Path

from pydantic import JsonValue

def generate_network_visualizations(
    parsed_data: dict[str, JsonValue], output_dir: Path, model_name: str
) -> list[str]: ...
