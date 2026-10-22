# Copyright (c) 2026 Daniel Ari Friedman
"""Render declarative graphical abstracts with manuscript-bound scientific quantities."""

import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import fill
from typing import ClassVar, Final, Literal, Protocol, TypedDict, Unpack

import matplotlib.pyplot as plt
import yaml
from matplotlib.figure import Figure
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from matplotlib.text import Text
from matplotlib.transforms import Bbox
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.concept_figures import draw_concept_operation
from thanks_for_nothing.concepts import CONCEPTS
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.figure_geometry import require_text_clearance
from thanks_for_nothing.figure_keys import draw_canvas
from thanks_for_nothing.gnn_graphs import GraphCatalog, ModelGraph
from thanks_for_nothing.manuscript_composition import ManuscriptLedger
from thanks_for_nothing.manuscript_literals import require_injected_numbers
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.visual_style import PlotAxes, figure
from thanks_for_nothing.visual_tokens import PALETTE

_SHORT_ROUTE_NODES: Final = 3


class _Panel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)
    title: str = Field(min_length=1)
    question: str = Field(min_length=1)
    route: tuple[str, str, str]
    finding: str = Field(min_length=1)
    qualification: str = Field(min_length=1)
    anchor: str = Field(pattern=r"^[a-z][a-z0-9-]+$")
    symbol: Literal["A", "B", "C", "D"] | None = None
    link_label: str | None = None
    model_family: str | None = None


class AbstractPage(BaseModel):
    """One authored portrait page with explicit operations, claims and qualifications."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)
    key: str = Field(pattern=r"^[a-z]+$")
    kicker: str = Field(min_length=1)
    title: str = Field(min_length=1)
    subtitle: str = Field(min_length=1)
    panels: tuple[_Panel, ...]
    bridge_title: str = Field(min_length=1)
    bridge: tuple[str, str, str, str, str, str]
    note: str = Field(min_length=1)
    scope: str = Field(min_length=1)


class _Pages(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)
    pages: tuple[AbstractPage, AbstractPage]


@dataclass(frozen=True, slots=True)
class AbstractArtifact:
    """A front-matter image and its exact configuration, scalar and output bindings."""

    key: str
    title: str
    alt: str
    pdf: str
    png: str
    svg: str
    pdf_sha256: str
    png_sha256: str
    svg_sha256: str
    links: tuple[tuple[str, str], ...]


class _Manifest(BaseModel):
    configuration_sha256: str
    variables_sha256: str
    graphs_sha256: str
    pages: tuple[AbstractArtifact, ...]


class _TextStyle(TypedDict, total=False):
    size: float
    width: int
    color: str
    bold: bool


class _AbstractExport(Protocol):
    def savefig(
        self, fname: Path, *, dpi: float = ..., facecolor: str, metadata: dict[str, str | None] = ...
    ) -> None: ...


def abstract_pages(root: Path, output: Path) -> tuple[AbstractPage, AbstractPage]:
    """Resolve only admitted scalar tokens and reject missing links or scientific literals."""
    source = (root / "docs/manuscript/graphical-abstracts.yaml").read_text()
    require_injected_numbers(source)
    ledger = TypeAdapter(ManuscriptLedger).validate_json(
        (output / "reports/manuscript_variables.json").read_text()
    )
    variables = {row.name: row.value for row in ledger.variables}
    used = {match[1] for match in re.finditer(r"\{\{([A-Z][A-Z0-9_]*)\}\}", source)}
    if used - variables.keys():
        message = "Unresolved graphical abstract scientific quantity"
        raise ContractError(message)
    for name in used:
        source = source.replace("{{" + name + "}}", str(variables[name]))
    pages = _Pages.model_validate(yaml.safe_load(source)).pages
    if tuple(page.key for page in pages) != ("meanings", "experiments"):
        message = "Graphical abstract pages must be meanings then experiments"
        raise ContractError(message)
    if tuple(len(page.panels) for page in pages) != (4, 6):
        message = "Graphical abstracts require four conceptual and six experimental comparisons"
        raise ContractError(message)
    manuscript = (output / "reports/manuscript.md").read_text()
    if any(f"{{#{panel.anchor}" not in manuscript for page in pages for panel in page.panels):
        message = "Graphical abstract points to a missing manuscript section"
        raise ContractError(message)
    return pages


def _text(ax: PlotAxes, x: float, y: float, text: str, **style: Unpack[_TextStyle]) -> None:
    artist = ax.text(
        x,
        y,
        fill(text, style.get("width", 100)),
        fontsize=style.get("size", 10),
        ha="left",
        va="top",
        color=style.get("color", PALETTE["ink"]),
        weight="bold" if style.get("bold", False) else "normal",
        linespacing=1.4,
        transform=ax.transAxes,
    )
    width = style.get("width", 100)
    available = ax.transAxes.transform_bbox(Bbox.from_extents(x, 0, 0.96, 1)).width
    while artist.get_window_extent().width > available and width > 1:
        width -= 1
        artist.set_text(fill(text, width))


def _route(
    ax: PlotAxes, labels: tuple[str, ...], y: float, *, color: str, height: float = 0.045
) -> None:
    left, right = 0.045, 0.955
    step = (right - left) / len(labels)
    for index, label in enumerate(labels):
        x = left + index * step
        _ = ax.add_patch(
            FancyBboxPatch(
                (x, y - height),
                step - 0.018,
                height,
                boxstyle="round,pad=0.004,rounding_size=0.004",
                edgecolor=color,
                facecolor="white",
                linewidth=0.8,
                transform=ax.transAxes,
            )
        )
        _ = ax.text(
            x + 0.01,
            y - 0.009,
            fill(label, 27 if len(labels) == _SHORT_ROUTE_NODES else 13),
            fontsize=9.2 if len(labels) == _SHORT_ROUTE_NODES else 8.7,
            va="top",
            color=PALETTE["ink"],
            linespacing=1.25,
            transform=ax.transAxes,
        )
        if index < len(labels) - 1:
            _ = ax.add_patch(
                FancyArrowPatch(
                    (x + step - 0.016, y - height / 2),
                    (x + step - 0.002, y - height / 2),
                    arrowstyle="-|>",
                    mutation_scale=8,
                    color=color,
                    linewidth=0.9,
                    transform=ax.transAxes,
                )
            )


def _draw(page: AbstractPage, catalog: GraphCatalog) -> Figure:
    if page.key == "experiments":
        return _experimental_page(page, catalog)
    fig, ax = figure(7.8, 10.7 / 1.1, automatic_layout=False)
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.015, top=0.985)
    _ = ax.set(xlim=(0, 1), ylim=(0, 1))
    _ = ax.axis("off")
    colors = ("#007C83", "#526277", "#946019", "#63518B")
    _text(ax, 0.035, 0.988, page.kicker, size=9.5, color=colors[0], bold=True)
    _text(ax, 0.035, 0.955, page.title, size=20.5, width=43, bold=True)
    _text(ax, 0.035, 0.909, page.subtitle, size=10.3, width=100)
    for index, panel in enumerate(page.panels):
        top = (0.836 - index * 0.154) if page.key == "meanings" else (0.848 - index * 0.166)
        color = colors[index]
        if panel.symbol is not None:
            color = PALETTE[next(concept.role for concept in CONCEPTS if concept.code == panel.symbol)]
        _ = ax.add_patch(
            FancyBboxPatch(
                (0.025, top - (0.150 if page.key == "meanings" else 0.162)),
                0.95,
                0.150 if page.key == "meanings" else 0.162,
                boxstyle="round,pad=0.004,rounding_size=0.005",
                facecolor="#F6F8F9",
                edgecolor="#DCE4E8",
                linewidth=0.65,
                transform=ax.transAxes,
            )
        )
        if panel.symbol is not None:
            glyph = fig.add_subplot()
            glyph.set_position((0.055, 0.015 + 0.97 * (top - 0.142), 0.205, 0.118))
            draw_concept_operation(glyph, panel.symbol)
            _text(ax, 0.29, top - 0.012, panel.title, size=12.0, color=color, bold=True)
            _text(ax, 0.29, top - 0.040, panel.question, size=8.6, width=80, color="#485B67")
            _text(ax, 0.29, top - 0.068, panel.finding, size=9.2, width=78, bold=True)
            _text(ax, 0.29, top - 0.116, panel.qualification, size=8.6, width=85, color="#485B67")
        else:
            _text(ax, 0.045, top - 0.007, panel.title, size=12.0, color=color, bold=True)
            _text(ax, 0.045, top - 0.033, panel.question, size=8.2, width=115, color="#485B67")
            _route(ax, panel.route, top - 0.056, color=color, height=0.040)
            _text(ax, 0.045, top - 0.103, panel.finding, size=9.2, width=100, bold=True)
            _text(ax, 0.045, top - 0.142, panel.qualification, size=8.5, width=115, color="#485B67")
    bridge_y, route_y, note_y, line_y, scope_y = (
        (0.209, 0.178, 0.102, 0.042, 0.033)
        if page.key == "meanings"
        else (0.172, 0.142, 0.076, 0.034, 0.024)
    )
    _text(ax, 0.035, bridge_y, page.bridge_title, size=11.5, bold=True)
    _route(ax, page.bridge, route_y, color=colors[0], height=0.052)
    _text(ax, 0.035, note_y, page.note, size=9.2, width=115)
    _ = ax.plot((0.035, 0.965), (line_y, line_y), color="#CCD7DC", linewidth=0.8)
    _text(ax, 0.035, scope_y, page.scope, size=9.2, width=115, bold=True)
    return fig


def _experimental_page(page: AbstractPage, catalog: GraphCatalog) -> Figure:
    fig, ax = figure(7.8, 10.7, automatic_layout=False)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    _ = ax.set(xlim=(0, 1), ylim=(0, 1))
    _ = ax.axis("off")
    _text(ax, 0.04, 0.978, page.kicker, size=10, bold=True)
    _text(ax, 0.04, 0.946, page.title, size=23, bold=True)
    _text(ax, 0.04, 0.901, page.subtitle, size=10, width=115)
    for index, panel in enumerate(page.panels):
        candidates = [
            m
            for m in catalog.models
            if m.model_id == panel.model_family or m.execution == f"Local / {panel.model_family}"
        ]
        if not candidates:
            message = f"Graphical abstract has no executed GNN model: {panel.model_family}"
            raise ContractError(message)
        top = 0.837 - index * 0.112
        _ = ax.plot((0.04, 0.96), (top + 0.008, top + 0.008), color=PALETTE["grid"], linewidth=0.8)
        glyph = fig.add_subplot()
        glyph.set_position((0.035, top - 0.095, 0.22, 0.09))
        glyph.set_gid(f"abstract_model_{panel.model_family}")
        _model_glyph(glyph, candidates[0])
        _text(ax, 0.29, top, panel.title, size=11.6, bold=True)
        _text(ax, 0.29, top - 0.028, panel.finding, size=9.2, width=83, bold=True)
        _text(ax, 0.29, top - 0.069, panel.qualification, size=8.9, width=86)
    _text(ax, 0.04, 0.153, page.bridge_title, size=11.2, bold=True)
    _route(ax, page.bridge, 0.123, color=PALETTE["positive_recall"], height=0.041)
    _text(ax, 0.04, 0.072, page.note, size=9.0, width=120)
    _text(ax, 0.04, 0.032, page.scope, size=9.0, width=120, bold=True)
    return fig


def _model_glyph(axis: PlotAxes, model: ModelGraph) -> None:
    variables = dict(model.variables)
    state = "z" if "z" in variables else "s"
    positions = {state: (0.23, 0.67), "o": (0.77, 0.67)}
    if "q" in variables:
        positions["q"] = (0.23, 0.24)
    for name, position in positions.items():
        _ = axis.add_patch(
            Circle(
                position,
                0.13,
                facecolor=PALETTE["grid"] if name == "o" else "white",
                edgecolor=PALETTE["positive_recall"],
                linewidth=1.4,
            )
        )
        _ = axis.text(*position, f"{name}[{variables[name][0]}]", fontsize=9, va="center", ha="center")
    for source in (state, *(("q",) if "q" in positions else ())):
        _ = axis.add_patch(
            FancyArrowPatch(
                positions[source],
                positions["o"],
                arrowstyle="-|>",
                shrinkA=15,
                shrinkB=15,
                mutation_scale=12,
                color=PALETTE["ink"],
                linewidth=1.2,
            )
        )
    shape = dict(model.tensor_shapes)["A"]
    _ = axis.text(0.5, 0.02, "A: " + " x ".join(map(str, shape)), fontsize=8.8, ha="center")
    _ = axis.set(xlim=(0, 1), ylim=(0, 1))
    _ = axis.axis("off")


def _export(fig: _AbstractExport, paths: dict[str, Path]) -> None:
    fig.savefig(paths["png"], dpi=220, facecolor="white")
    fig.savefig(paths["svg"], facecolor="white", metadata={"Date": None})
    fig.savefig(paths["pdf"], facecolor="white", metadata={"CreationDate": None, "ModDate": None})


draw_frontmatter_text = _text
export_frontmatter = _export
FrontmatterTextStyle = _TextStyle


def write_graphical_abstracts(root: Path, output: Path) -> tuple[AbstractArtifact, ...]:
    """Export both full-page vector/raster images and preserve their source and value custody."""
    pages = abstract_pages(root, output)
    catalog = TypeAdapter(GraphCatalog).validate_json((output / "data/gnn_graphs.json").read_text())
    directory = output / "frontmatter"
    directory.mkdir(parents=True, exist_ok=True)
    artifacts: list[AbstractArtifact] = []
    for page in pages:
        paths = {
            suffix: directory / f"graphical-abstract-{page.key}.{suffix}"
            for suffix in ("pdf", "png", "svg")
        }
        fig = _draw(page, catalog)
        try:
            draw_canvas(fig.canvas)
            require_text_clearance(fig)
            texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text()]
            for index, text in enumerate(texts):
                if any(
                    text.get_window_extent().overlaps(other.get_window_extent())
                    for other in texts[index + 1 :]
                ):
                    message = f"Graphical abstract text overlaps: {text.get_text()!r}"
                    raise ContractError(message)
            _export(fig, paths)
        finally:
            plt.close(fig)
        artifacts.append(
            AbstractArtifact(
                page.key,
                page.title,
                " ".join(
                    [
                        page.subtitle,
                        *(f"{p.title}: {p.question} {p.finding} {p.qualification}" for p in page.panels),
                        page.note,
                        page.scope,
                    ]
                ),
                pdf=str(paths["pdf"].relative_to(output)),
                png=str(paths["png"].relative_to(output)),
                svg=str(paths["svg"].relative_to(output)),
                pdf_sha256=file_digest(paths["pdf"]),
                png_sha256=file_digest(paths["png"]),
                svg_sha256=file_digest(paths["svg"]),
                links=tuple((panel.link_label or panel.title, panel.anchor) for panel in page.panels),
            )
        )
    write_record(
        output / "reports/graphical_abstracts.json",
        _Manifest(
            configuration_sha256=file_digest(root / "docs/manuscript/graphical-abstracts.yaml"),
            variables_sha256=file_digest(output / "reports/manuscript_variables.json"),
            graphs_sha256=file_digest(output / "data/gnn_graphs.json"),
            pages=tuple(artifacts),
        ),
    )
    return tuple(artifacts)


def graphical_abstracts_valid(root: Path, output: Path) -> bool:
    """Reject omitted, reordered, stale or altered front-matter images."""
    path = output / "reports/graphical_abstracts.json"
    if not path.is_file():
        return False
    try:
        record = _Manifest.model_validate_json(path.read_text())
    except ValidationError:
        return False
    pages = abstract_pages(root, output)
    return (
        record.configuration_sha256 == file_digest(root / "docs/manuscript/graphical-abstracts.yaml")
        and record.variables_sha256 == file_digest(output / "reports/manuscript_variables.json")
        and record.graphs_sha256 == file_digest(output / "data/gnn_graphs.json")
        and [row.key for row in record.pages] == [page.key for page in pages]
        and all(
            (output / path).is_file() and file_digest(output / path) == digest
            for row in record.pages
            for path, digest in (
                (row.pdf, row.pdf_sha256),
                (row.png, row.png_sha256),
                (row.svg, row.svg_sha256),
            )
        )
    )
