# Copyright (c) 2026 Daniel Ari Friedman
"""Admit a selective textual comparison without inventing cross-tradition measurements."""

from pathlib import Path
from typing import Annotated, ClassVar, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.custody import InputFile
from thanks_for_nothing.provenance import file_digest

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TraditionRow(BaseModel):
    """One named witness, its interpretive comparison and its explicit evidential limit."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    tradition: Text
    witness: Text
    source_keys: tuple[Text, ...] = Field(min_length=1)
    absence: Text
    response: Text
    appreciation: Text
    practice: Text
    limit: Text
    comparison: Text


class TraditionSelection(BaseModel):
    """Authored qualitative rows; sequence is editorial, never a ranking or measured scale."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["thanks_for_nothing.traditions.v1"]
    scope: Text
    rows: tuple[TraditionRow, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def unique_rows(self) -> Self:
        """Reject ambiguous row identities and repeated source keys before rendering."""
        if len({row.id for row in self.rows}) != len(self.rows) or any(
            len(set(row.source_keys)) != len(row.source_keys) for row in self.rows
        ):
            message = "Tradition rows and their source keys must be unique"
            raise ValueError(message)
        return self


class TextSource(BaseModel):
    """Bibliographic identity and verified source URL projected from the scholarship catalog."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    key: Text
    title: Text
    url: HttpUrl

    @model_validator(mode="after")
    def require_https(self) -> Self:
        """Keep the source-linked companion within the catalog's HTTPS boundary."""
        if self.url.scheme != "https":
            message = "Tradition source URLs must use HTTPS"
            raise ValueError(message)
        return self


class TraditionsRecord(BaseModel):
    """Self-contained publication input bound to authored rows and source-catalog bytes."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["thanks_for_nothing.traditions_record.v1"]
    selection: TraditionSelection
    sources: tuple[TextSource, ...]
    inputs: tuple[InputFile, ...]

    @model_validator(mode="after")
    def source_closure(self) -> Self:
        """Require exactly the cited identities, with no missing or duplicate source record."""
        keys = {source.key for source in self.sources}
        used = {key for row in self.selection.rows for key in row.source_keys}
        if len(keys) != len(self.sources) or keys != used:
            message = "Tradition source identities do not close over the selected rows"
            raise ValueError(message)
        return self


class _Catalog(BaseModel):
    sources: tuple[TextSource, ...]


def build_traditions(root: Path) -> TraditionsRecord:
    """Resolve each authored citation against the actual catalog and bind both source files."""
    selection_path = root / "data/scholarship/traditions.json"
    catalog_path = root / "data/scholarship/sources.json"
    selection = TraditionSelection.model_validate_json(selection_path.read_text())
    catalog = _Catalog.model_validate_json(catalog_path.read_text()).sources
    indexed = {source.key: source for source in catalog}
    used = {key for row in selection.rows for key in row.source_keys}
    if len(indexed) != len(catalog) or not used <= indexed.keys():
        message = "Tradition selection has missing or ambiguous scholarship sources"
        raise ContractError(message)
    return TraditionsRecord(
        schema_version="thanks_for_nothing.traditions_record.v1",
        selection=selection,
        sources=tuple(indexed[key] for key in sorted(used)),
        inputs=tuple(
            InputFile(str(path.relative_to(root)), file_digest(path))
            for path in (selection_path, catalog_path)
        ),
    )


def write_traditions(root: Path, output: Path) -> TraditionsRecord:
    """Publish admitted comparison rows as a figure input without changing numerical records."""
    record = build_traditions(root)
    write_record(output / "data/world_traditions.json", record)
    return record


def traditions_valid(root: Path, output: Path) -> bool:
    """Reject stale or forged qualitative rows through exact source-bound replay."""
    recorded = TraditionsRecord.model_validate_json((output / "data/world_traditions.json").read_text())
    return recorded == build_traditions(root)
