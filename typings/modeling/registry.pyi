# Copyright (c) 2026 Daniel Ari Friedman
from typing import TypeAlias

JSONValue: TypeAlias = str | int | float | bool | list[JSONValue] | dict[str, JSONValue] | None

class ModelSpecification:
    model_id: str
    source_hash: str
    family: str
    backend: str
    consumer: str
    parameters: dict[str, JSONValue]
    tensors: dict[str, JSONValue]

def parse_model(content: str, model_id: str) -> ModelSpecification: ...
