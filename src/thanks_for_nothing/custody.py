# Copyright (c) 2026 Daniel Ari Friedman
"""Bind research inputs to the executing package and a deterministic source receipt."""

from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from typing import Final

from thanks_for_nothing import __version__
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.provenance import file_digest

INPUT_DIRECTORIES: Final = ("src", "scripts", "docs", "data", "notebooks", "typings")
INPUT_SUFFIXES: Final = frozenset(
    {
        ".py",
        ".pyi",
        ".md",
        ".json",
        ".yaml",
        ".bib",
        ".ipynb",
        ".docx",
        ".xml",
        ".html",
        ".pdf",
        ".txt",
        ".png",
        ".jpg",
        ".jpeg",
        ".lua",
        ".tex",
        ".css",
    }
)


@dataclass(frozen=True, slots=True)
class InputFile:
    """A repository-relative input path bound to its SHA-256."""

    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class SourceTreeReceipt:
    """Execution version and digest of declared inputs, excluding generated outputs."""

    schema: str
    package_version: str
    files: tuple[InputFile, ...]
    tree_sha256: str


def source_tree_receipt(root: Path) -> SourceTreeReceipt:
    """Admit source/package identity and hash scientific inputs without runtime caches."""
    paths = [root / "pyproject.toml", root / "uv.lock"]
    for name in INPUT_DIRECTORIES:
        paths.extend(
            path for path in (root / name).rglob("*") if path.is_file() and path.suffix in INPUT_SUFFIXES
        )
    package = root / "src/thanks_for_nothing"
    if not package.is_dir():
        message = "Research source root is missing the package"
        raise ContractError(message)
    for path in package.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".md"}:
            executing = Path(__file__).parent / path.relative_to(package)
            if not executing.is_file() or file_digest(executing) != file_digest(path):
                message = "Executing package contents differ from the declared research source root"
                raise ContractError(message)
    files = tuple(InputFile(str(path.relative_to(root)), file_digest(path)) for path in sorted(paths))
    payload = "".join(f"{file.path}\0{file.sha256}\n" for file in files).encode()
    actual = version("thanks-for-nothing")
    if actual != __version__:
        message = "Executing package and source version differ"
        raise ContractError(message)
    return SourceTreeReceipt(
        "thanks_for_nothing.source_tree.v1", actual, files, sha256(payload).hexdigest()
    )
