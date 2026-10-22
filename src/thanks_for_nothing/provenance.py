# Copyright (c) 2026 Daniel Ari Friedman
"""Independent source pins and executing-distribution identity for research receipts."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from hashlib import sha256
from importlib import import_module, metadata
from pathlib import Path
from typing import ClassVar, Final, Literal

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import override


@dataclass(frozen=True, slots=True)
class ProvenanceError(ValueError):
    """An independent artifact identity requirement was not met."""

    artifact: str
    reason: str

    @override
    def __str__(self) -> str:
        return f"{self.artifact}: {self.reason}"


@dataclass(frozen=True, slots=True)
class SourcePin:
    """Independent original source digest and retrieval provenance."""

    key: str
    path: str
    sha256: str
    url: str
    title: str
    license: str


SOURCE_PINS: Final = (
    SourcePin(
        "sandvedsmith2026noself",
        "data/sources/emptiness_preprint_v1.pdf",
        "94e2335c3a4a37b8d49039b11b45ccda25bad65d4b80aa15428b84abfba699ac",
        "https://osf.io/preprints/psyarxiv/m78z2_v1",
        "There is no self-evidence: A physics of emptiness realisation, version 1",
        "CC-BY-4.0",
    ),
    SourcePin(
        "fisher2025",
        "data/sources/gratitude_preprint_v1.docx",
        "f9ba1ed0e3e5ecff219348eccc322a1ee5156d001eba7eff87be91ac01a08e46",
        "https://osf.io/preprints/psyarxiv/xm25y_v1",
        "Computational mechanisms of gratitude practice, preprint version 1",
        "CC-BY-4.0",
    ),
    SourcePin(
        "source_belief_notebook",
        "data/sources/gratitude_original.ipynb",
        "1b8a0400ba6c457d1da8ca28a369f60be2f367fb760a794c78ce7125a321ceb6",
        "https://colab.research.google.com/drive/1OaYkfpko5RO1JIKgj-Ayb_tNfdTcmt0z",
        "Original 1000-agent gratitude belief-updating notebook",
        "not declared in notebook metadata",
    ),
    SourcePin(
        "source_attention_notebook",
        "data/sources/yarbus_original.ipynb",
        "ab9f36b515d1534d24b7e676841fa5cea7c264370f6ee566798c8b1b3de62510",
        "https://colab.research.google.com/drive/1D6KJIQgzZhpKOaX4WKgjWl10xG_ZoMdO",
        "Original Yarbus attention notebook linked by the preprint",
        "not declared in notebook metadata",
    ),
)


@dataclass(frozen=True, slots=True)
class DependencyPin:
    """Pinned distribution version, repository, commit and executing module."""

    distribution: str
    version: str
    repository: str
    commit: str
    module: str


DEPENDENCY_PINS: Final = (
    DependencyPin(
        "generalized-notation-notation",
        "4.1.0",
        "https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation",
        "46459949944e3217f8a6a804d4ff8c52829ef275",
        "gnn.parsers.markdown_parser",
    ),
    DependencyPin(
        "realizing-emptiness",
        "3.0.0",
        "https://github.com/docxology/realizing_emptiness",
        "bd91fa1c230551180ed741d1951840e3628da35d",
        "modeling.registry",
    ),
)


class _VcsInfo(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    commit_id: str
    vcs: Literal["git"]


class _DirectUrl(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    url: str
    vcs_info: _VcsInfo


class _ManifestSource(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    key: str
    path: str
    sha256: str


class _SourceManifest(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    schema_version: Literal["thanks_for_nothing.source_manifest.v1"] = Field(alias="schema")
    sources: tuple[_ManifestSource, ...]


@dataclass(frozen=True, slots=True)
class DependencyReceipt:
    """Verified installed dependency identity and executing source digest."""

    distribution: str
    version: str
    repository: str
    commit: str
    module: str
    module_sha256: str


@dataclass(frozen=True, slots=True)
class SourceReceipt:
    """Verified source bytes with their independent identity."""

    key: str
    path: str
    sha256: str
    bytes: int


@dataclass(frozen=True, slots=True)
class ProvenanceAudit:
    """Admitted sources and executing dependencies for a reproducible run."""

    schema: str
    sources: tuple[SourceReceipt, ...]
    dependencies: tuple[DependencyReceipt, ...]
    template_repository: str
    template_commit: str
    controls: dict[str, bool]


def file_digest(path: Path) -> str:
    """Hash the actual file bytes with SHA256."""
    return sha256(path.read_bytes()).hexdigest()


def executing_dependency(pin: DependencyPin) -> DependencyReceipt:
    """Verify both installed VCS identity and the actual executing module path."""
    distribution = metadata.distribution(pin.distribution)
    raw = distribution.read_text("direct_url.json")
    if raw is None:
        raise ProvenanceError(pin.distribution, "installed VCS receipt is missing")
    direct = _DirectUrl.model_validate_json(raw)
    if (
        distribution.version != pin.version
        or direct.vcs_info.commit_id != pin.commit
        or direct.url.removesuffix(".git") != pin.repository
    ):
        raise ProvenanceError(pin.distribution, "installed version or VCS identity differs from the pin")
    executing = Path(inspect.getfile(import_module(pin.module))).resolve()
    expected = Path(
        str(distribution.locate_file(Path(*pin.module.split(".")).with_suffix(".py")))
    ).resolve()
    if executing != expected:
        raise ProvenanceError(pin.module, "executing module is not from the admitted distribution")
    return DependencyReceipt(
        pin.distribution,
        distribution.version,
        pin.repository,
        pin.commit,
        pin.module,
        file_digest(executing),
    )


def build_provenance_audit(root: Path) -> ProvenanceAudit:
    """Admit original source bytes and executing dependency identities."""
    receipts: list[SourceReceipt] = []
    for pin in SOURCE_PINS:
        path = root / pin.path
        if not path.is_file() or file_digest(path) != pin.sha256:
            raise ProvenanceError(pin.path, "source bytes differ from the independent original digest")
        receipts.append(SourceReceipt(pin.key, pin.path, pin.sha256, path.stat().st_size))
    manifest_path = root / "data/sources/source_manifest.json"
    manifest = _SourceManifest.model_validate_json(manifest_path.read_text())
    declared = {(row.key, row.path, row.sha256) for row in manifest.sources}
    expected = {(pin.key, pin.path, pin.sha256) for pin in SOURCE_PINS}
    if declared != expected or len(manifest.sources) != len(SOURCE_PINS):
        msg = "source_manifest.json"
        raise ProvenanceError(msg, "manifest does not match independently pinned source inventory")
    return ProvenanceAudit(
        "thanks_for_nothing.provenance.v1",
        tuple(receipts),
        tuple(executing_dependency(pin) for pin in DEPENDENCY_PINS),
        "https://github.com/docxology/template_code_project",
        "04040a1e8eda0b31ce61db888cd1b3598f1696ca",
        {
            "original_sources_unchanged": True,
            "source_manifest_matches_independent_pins": True,
            "executing_dependencies_match_pins": True,
        },
    )
