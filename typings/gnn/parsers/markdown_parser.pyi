# Copyright (c) 2026 Daniel Ari Friedman
from pydantic import JsonValue

class _Model:
    def to_dict(self) -> dict[str, JsonValue]: ...

class _Result:
    success: bool
    errors: list[str]
    warnings: list[str]
    model: _Model

class MarkdownGNNParser:
    def parse_string(self, content: str) -> _Result: ...
