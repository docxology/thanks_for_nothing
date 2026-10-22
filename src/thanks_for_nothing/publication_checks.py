# Copyright (c) 2026 Daniel Ari Friedman
"""Replay numbering and author metadata against the generated publication source."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

from typing_extensions import override

from thanks_for_nothing.artifact_checks import read_record
from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.formalisms import FormalismRegistry, build_formalism_registry
from thanks_for_nothing.gnn_model_card import gnn_model_card_valid
from thanks_for_nothing.graphical_abstracts import graphical_abstracts_valid
from thanks_for_nothing.illustrations import IllustrationRegistry, build_illustration_registry
from thanks_for_nothing.manuscript_composition import ManuscriptLedger, compose_source
from thanks_for_nothing.publication import load_publication
from thanks_for_nothing.reporting import hydration


class _PublicationHtml(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.fragments: list[str] = []
        self.inside_cover: bool = False
        self.identifiers: list[str] = []
        self.references: list[str] = []
        self.cover_links: list[str] = []
        self.reading_order: list[str] = []
        self.inside_contents: bool = False
        self.contents_references: list[str] = []
        self.equations: list[tuple[str | None, str | None]] = []
        self.figures: list[tuple[str | None, str | None]] = []
        self.caption_checks: list[bool] = []
        self.figure_number: str | None = None
        self.inside_caption: bool = False
        self.caption_fragments: list[str] = []

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        identifier = attributes.get("id")
        self._record_reading_order(tag, identifier)
        if identifier is not None:
            self.identifiers.append(identifier)
        href = attributes.get("href")
        if href is not None and self.inside_cover:
            self.cover_links.append(href)
        if href is not None and href.startswith("#") and len(href) > 1:
            self.references.append(unquote(href[1:]))
            if self.inside_contents:
                self.contents_references.append(unquote(href[1:]))
        if "formalism" in (attributes.get("class") or "").split():
            self.equations.append((identifier, attributes.get("data-equation-number")))
        if tag == "figure":
            self.figure_number = attributes.get("data-figure-number")
            if self.figure_number is not None:
                self.figures.append((identifier, self.figure_number))
        if tag == "figcaption" and self.figure_number is not None:
            self.inside_caption = True
            self.caption_fragments = []
        if tag == "header" and identifier == "title-block-header":
            self.inside_cover = True

    def _record_reading_order(self, tag: str, identifier: str | None) -> None:
        if tag == "figure" and identifier in {
            "graphical-abstract-meanings",
            "graphical-abstract-experiments",
            "graphical-abstract-modelcard",
        }:
            self.reading_order.append(identifier)
        if tag == "header" and identifier == "title-block-header":
            self.reading_order.append("cover")
        if tag == "nav" and identifier == "TOC":
            self.reading_order.append("contents")
            self.inside_contents = True
        if tag == "main":
            self.reading_order.append("manuscript")

    @override
    def handle_endtag(self, tag: str) -> None:
        if tag == "nav":
            self.inside_contents = False
        if tag == "header":
            self.inside_cover = False
        if tag == "figcaption" and self.inside_caption:
            caption = " ".join(" ".join(self.caption_fragments).split())
            self.caption_checks.append(caption.startswith(f"Figure {self.figure_number}. "))
            self.inside_caption = False
        if tag == "figure":
            self.figure_number = None

    @override
    def handle_data(self, data: str) -> None:
        if self.inside_cover:
            self.fragments.append(data)
        if self.inside_caption:
            self.caption_fragments.append(data)


def publication_valid(root: Path, output: Path, *, require_render: bool) -> bool:
    """Require stable equation identities and consistent author/DOI metadata in rendered HTML."""
    metadata = load_publication(root)
    manuscript = (output / "reports/manuscript.md").read_text()
    registry = build_formalism_registry(manuscript)
    illustrations = build_illustration_registry(manuscript)
    if (
        not registry.entries
        or read_record(output / "reports/formalisms.json", FormalismRegistry) != registry
        or read_record(output / "reports/illustrations.json", IllustrationRegistry) != illustrations
    ):
        return False
    if not require_render:
        return True
    if metadata.graphical_abstracts and (
        not graphical_abstracts_valid(root, output) or not gnn_model_card_valid(output)
    ):
        return False
    html_path = output / "manuscript.html"
    if not html_path.is_file():
        return False
    html = html_path.read_text()
    parser = _PublicationHtml()
    parser.feed(html)
    parser.close()
    cover = " ".join(" ".join(parser.fragments).split())
    return (
        all(
            value in cover
            for value in (
                metadata.title,
                metadata.cover_kicker,
                metadata.cover_summary,
                metadata.author[0],
                metadata.orcid,
                metadata.doi_display,
                metadata.paper_license,
                metadata.code_license,
            )
        )
        and parser.equations == [(entry.label, str(entry.number)) for entry in registry.entries]
        and parser.reading_order
        == [
            "cover",
            *(
                [
                    "graphical-abstract-meanings",
                    "graphical-abstract-experiments",
                    "graphical-abstract-modelcard",
                ]
                if metadata.graphical_abstracts
                else []
            ),
            "contents",
            "manuscript",
        ]
        and bool(parser.contents_references)
        and (metadata.doi_url is None or metadata.doi_url in parser.cover_links)
        and f"https://orcid.org/{metadata.orcid}" in parser.cover_links
        and metadata.paper_license_url in parser.cover_links
        and metadata.repository_url in parser.cover_links
        and parser.figures == [(entry.label, str(entry.number)) for entry in illustrations.entries]
        and len(parser.caption_checks) == len(illustrations.entries)
        and all(parser.caption_checks)
        and len(parser.identifiers) == len(set(parser.identifiers))
        and set(parser.references) <= set(parser.identifiers)
    )


def manuscript_variables_valid(root: Path, output: Path) -> bool:
    """Reject stale supplements, forged injected values and unreplayed source bindings."""
    bundle = read_bundle(output)
    expected, ledger = compose_source(
        root, output, bundle, {row.token: row.text for row in hydration(bundle)}
    )
    return (output / "reports/manuscript.md").read_text() == expected and read_record(
        output / "reports/manuscript_variables.json", ManuscriptLedger
    ) == ledger
