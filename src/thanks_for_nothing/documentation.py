# Copyright (c) 2026 Daniel Ari Friedman
"""Offline documentation inventory, index coverage and local-reference closure."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from thanks_for_nothing.custody import InputFile
from thanks_for_nothing.provenance import file_digest


@dataclass(frozen=True, slots=True)
class DocumentationIssue:
    """A local reference or discoverability failure requiring an authoring fix."""

    source: str
    target: str
    reason: str


@dataclass(frozen=True, slots=True)
class DocumentationAudit:
    """Exact documentation inputs and the bounded result of local-reference checks."""

    schema: str
    inputs: tuple[InputFile, ...]
    local_links: int
    issues: tuple[DocumentationIssue, ...]
    excluded_products: tuple[str, ...]
    all_pass: bool


@dataclass(frozen=True, slots=True)
class DocumentationContext:
    """Research source, product directory and explicitly requested rendering scope."""

    root: Path
    output: Path
    include_rendered: bool = True


@dataclass(frozen=True, slots=True)
class _LocalLink:
    source: str
    target: str
    destination: Path
    reason: str
    excluded: bool


def _prose(path: Path) -> str:
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", path.read_text())


def _fragments(path: Path) -> frozenset[str]:
    paths = (path,)
    if path.name in {"manuscript.md", "supplement.md"} and path.parent.name == "manuscript":
        paths = tuple(path.parent / name for name in ("manuscript.md", "supplement.md"))
    text = "\n".join(_prose(p) for p in paths if p.is_file())
    explicit = set(re.findall(r"\{#([^\s}]+)", text)) | set(re.findall(r"\\label\{([^}]+)\}", text))
    headings = {
        re.sub(r"[^\w\s-]", "", re.sub(r"\s*\{[^}]*\}\s*$", "", match[1]))
        .strip()
        .lower()
        .replace(" ", "-")
        for match in re.finditer(r"(?m)^#{1,6}\s+(.+)$", text)
    }
    return frozenset(explicit | headings)


def _inspect_link(context: DocumentationContext, source: Path, raw: str) -> _LocalLink | None:
    target = urlsplit(raw)
    if target.scheme or target.netloc:
        return None
    relative = unquote(target.path)
    destination = (
        (
            context.root / relative if relative.startswith("output/") else source.parent / relative
        ).resolve()
        if relative
        else source
    )
    is_product = destination.is_relative_to(context.root / "output")
    if is_product:
        destination = context.output / destination.relative_to(context.root / "output")
    excluded = (
        is_product
        and not context.include_rendered
        and destination in {context.output / "manuscript.pdf", context.output / "manuscript.html"}
    )
    reason = ""
    if not is_product and not destination.is_relative_to(context.root):
        reason = "local target leaves the repository"
    elif not excluded and not destination.exists():
        reason = "local target does not exist"
    elif (
        target.fragment
        and destination.suffix == ".md"
        and unquote(target.fragment) not in _fragments(destination)
    ):
        reason = "Markdown fragment does not exist"
    return _LocalLink(str(source.relative_to(context.root)), raw, destination, reason, excluded)


def documentation_audit(
    root: Path, *, output: Path | None = None, include_rendered: bool = True
) -> DocumentationAudit:
    """Check local targets and guide discoverability without claiming semantic or web verification."""
    root = root.resolve()
    context = DocumentationContext(root, (output or root / "output").resolve(), include_rendered)
    paths = tuple(sorted((root / "docs").rglob("*.md"))) + tuple(
        root / name
        for name in ("README.md", "AGENTS.md", "CONTEXT.md", "DESIGN.md")
        if (root / name).is_file()
    )
    links = tuple(
        link
        for path in paths
        for match in re.finditer(r"!?\[[^\]\n]*\]\(([^\s)]+)\)", _prose(path))
        if (link := _inspect_link(context, path, match[1])) is not None
    )
    issues = [DocumentationIssue(link.source, link.target, link.reason) for link in links if link.reason]
    indexed = {link.destination for link in links if link.source == "docs/README.md"}
    issues.extend(
        DocumentationIssue("docs/README.md", str(guide.relative_to(root)), "guide is not indexed")
        for guide in sorted((root / "docs").glob("*.md"))
        if guide.name != "README.md" and guide.resolve() not in indexed
    )
    if not (root / "docs/README.md").is_file():
        issues.append(DocumentationIssue("docs/README.md", "", "documentation index is missing"))
    return DocumentationAudit(
        "thanks_for_nothing.documentation.v1",
        tuple(InputFile(str(path.relative_to(root)), file_digest(path)) for path in paths),
        len(links),
        tuple(issues),
        tuple(
            sorted(
                {str(link.destination.relative_to(context.output)) for link in links if link.excluded}
            )
        ),
        not issues,
    )
