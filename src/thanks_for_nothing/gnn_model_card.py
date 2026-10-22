# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound Bayesian front matter and complete, executable-declaration model cards."""

import base64
import inspect
from dataclasses import dataclass
from html import escape
from importlib.metadata import distribution
from pathlib import Path
from typing import Unpack

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.text import Text
from pydantic import JsonValue, TypeAdapter, ValidationError

from thanks_for_nothing.artifacts import record_json, write_record
from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.figure_geometry import require_text_clearance
from thanks_for_nothing.figure_keys import draw_canvas
from thanks_for_nothing.gnn_figures import draw_declaration_graph
from thanks_for_nothing.gnn_graphs import (
    GraphAsset,
    GraphCatalog,
    ModelGraph,
    expected_graphs,
    graph_model_path,
)
from thanks_for_nothing.graphical_abstracts import (
    AbstractArtifact,
    FrontmatterTextStyle,
    draw_frontmatter_text,
    export_frontmatter,
)
from thanks_for_nothing.product_contracts import REQUIRED_SPECIFICATION_NAMES
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.specifications import Tensors, load_model
from thanks_for_nothing.visual_style import PALETTE, PlotAxes, figure


@dataclass(frozen=True, slots=True)
class _Card:
    graph: ModelGraph
    tensors: Tensors
    parameters: dict[str, JsonValue]
    declaration: str
    native_assets: tuple[GraphAsset, ...]


@dataclass(frozen=True, slots=True)
class _Document:
    schema: str
    catalog_sha256: str
    parser_sha256: str
    renderer_sha256: str
    generator_sha256: str
    dependencies: dict[str, dict[str, JsonValue]]
    cards: tuple[_Card, ...]


@dataclass(frozen=True, slots=True)
class _Receipt:
    document_sha256: str
    artifact: AbstractArtifact
    companion_sha256: str


def model_card_document(output: Path) -> _Document:
    """Require every catalog row to match the declaration actually consumed by its experiment."""
    catalog = TypeAdapter(GraphCatalog).validate_json((output / "data/gnn_graphs.json").read_text())
    bundle = read_bundle(output)
    expected = expected_graphs(output, bundle)
    if catalog.models != expected:
        message = "Model-card catalog differs from admitted numerical consumers"
        raise ContractError(message)
    dependencies: dict[str, dict[str, JsonValue]] = {}
    for name in ("generalized-notation-notation", "realizing-emptiness", "inferactively-pymdp"):
        package = distribution(name)
        origin = package.read_text("direct_url.json")
        dependencies[name] = {
            "version": package.version,
            "origin": TypeAdapter(JsonValue).validate_json(origin) if origin else None,
        }
    cards: list[_Card] = []
    for graph in catalog.models:
        declaration = graph_model_path(output, graph.model_id)
        model = load_model(graph.model_id, declaration.parent)
        assets = tuple(a for a in catalog.assets if Path(a.path).parent.name == graph.model_id)
        if not assets or any(file_digest(output / a.path) != a.sha256 for a in assets):
            message = f"Model-card native assets are missing or altered: {graph.model_id}"
            raise ContractError(message)
        cards.append(
            _Card(
                graph,
                model.tensors,
                TypeAdapter(dict[str, JsonValue]).validate_json(model.parameters_json),
                declaration.read_text(),
                assets,
            )
        )
    return _Document(
        "thanks_for_nothing.gnn_model_card.v1",
        file_digest(output / "data/gnn_graphs.json"),
        catalog.parser_sha256,
        catalog.renderer_sha256,
        file_digest(Path(inspect.getfile(model_card_document))),
        dependencies,
        tuple(cards),
    )


def _bayesian_graph(axis: PlotAxes) -> None:
    positions = {
        "$s_t$": (0.27, 0.58),
        "$s_{t+1}$": (0.76, 0.58),
        "$o_t$": (0.27, 0.17),
        "$o_{t+1}$": (0.76, 0.17),
        "$u_t$": (0.53, 0.9),
    }
    for source, target in (
        ("$s_t$", "$s_{t+1}$"),
        ("$u_t$", "$s_{t+1}$"),
        ("$s_t$", "$o_t$"),
        ("$s_{t+1}$", "$o_{t+1}$"),
    ):
        _ = axis.add_patch(
            FancyArrowPatch(
                positions[source],
                positions[target],
                arrowstyle="-|>",
                mutation_scale=16,
                shrinkA=22,
                shrinkB=22,
                linewidth=1.6,
                color=PALETTE["ink"],
            )
        )
    for name, position in positions.items():
        observed = name.startswith("$o")
        _ = axis.add_patch(
            Circle(
                position,
                0.065,
                facecolor=PALETTE["grid"] if observed else "white",
                edgecolor=PALETTE["positive_recall"],
                linewidth=1.8,
            )
        )
        _ = axis.text(*position, name, ha="center", va="center", fontsize=15)
    for x, y, label in ((0.5, 0.47, "$B$"), (0.13, 0.35, "$A$"), (0.9, 0.35, "$A$")):
        _ = axis.text(x, y, label, fontsize=12, ha="center")
    _ = axis.set(xlim=(0, 1), ylim=(0, 1))
    _ = axis.axis("off")


def _text(axis: PlotAxes, x: float, y: float, text: str, **style: Unpack[FrontmatterTextStyle]) -> None:
    draw_frontmatter_text(axis, x, y, " ".join(text.split()), **style)


def _draw(document: _Document) -> Figure:
    fig, ax = figure(7.8, 10.7, automatic_layout=False)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    _ = ax.set(xlim=(0, 1), ylim=(0, 1))
    _ = ax.axis("off")
    _text(ax, 0.04, 0.975, "GNN / BAYESIAN MODEL CARD", size=10, bold=True)
    _text(ax, 0.04, 0.943, "From declarations to executed models", size=23, bold=True)
    _text(
        ax,
        0.04,
        0.9,
        "A time-unrolled POMDP view, parsed dependencies and the complete consumer inventory.",
        size=10.2,
    )
    _text(ax, 0.04, 0.86, "BAYESIAN TIME SLICE / conditional on the selected action", size=10, bold=True)
    graph = fig.add_subplot()
    graph.set_position((0.04, 0.625, 0.49, 0.22))
    _bayesian_graph(graph)
    for index, meaning in enumerate(
        (
            "A  observation | state",
            "B  next state | state, action",
            "D  initial-state prior",
            "C  log outcome preferences",
        )
    ):
        _text(ax, 0.56, 0.82 - index * 0.025, meaning, size=10, width=42)
    _text(
        ax,
        0.56,
        0.709,
        """Shaded: observations. Open: latent states and the conditioned action.
        D initializes the first state; C guides native policy selection,
        outside this conditional DAG.""",
        size=9.1,
        width=48,
    )
    factors = (
        r"$P(s_{0:T},o_{0:T}\mid u_{0:T-1},A,B,D)=D(s_0)",
        r"\prod_{t=0}^{T}A(o_t\mid s_t)\prod_{t=0}^{T-1}B(s_{t+1}\mid s_t,u_t)$",
    )
    _text(
        ax,
        0.04,
        0.614,
        "".join(factors),
        size=10,
        width=150,
    )
    _text(
        ax,
        0.04,
        0.578,
        "DECLARATION GRAPH / source structure, not an instantaneous causal DAG",
        size=10,
        bold=True,
    )
    groups: dict[tuple[tuple[str, ...], tuple[tuple[str, str, bool], ...]], list[_Card]] = {}
    for card in document.cards:
        key = (
            tuple(n for n, _ in card.graph.variables),
            tuple((e.source, e.target, e.directed) for e in card.graph.edges),
        )
        groups.setdefault(key, []).append(card)
    query_groups = [cards for cards in groups.values() if "q" in dict(cards[0].graph.variables)]
    for cards in query_groups[:1]:
        graph_axis = fig.add_subplot()
        graph_axis.set_position((0.04, 0.418, 0.46, 0.145))
        draw_declaration_graph(graph_axis, cards[0].graph, node_margin_points=7)
    _text(
        ax,
        0.54,
        0.55,
        "".join(
            (
                f"{len(document.cards)} declarations; {len(groups)} topology groups. ",
                "Complete query graph shown. B advances time; q and z define the joint basis. ",
                "Full models are linked below.",
            )
        ),
        size=9.3,
        width=49,
    )
    _text(
        ax,
        0.54,
        0.474,
        """The Bayesian diagram defines the tensor semantics. Finite consumers add their own
        declared task laws; a shared backend label does not establish native execution.""",
        size=9.3,
        width=49,
    )
    _text(
        ax,
        0.04,
        0.402,
        "AUTHORING INPUTS / complete executed instances in the linked cards",
        size=10,
        bold=True,
    )
    columns = (0.04, 0.46, 0.59, 0.74, 0.85, 0.94)
    for x, label in zip(columns, ("Declaration / consumer", "A", "B", "C", "D", "SHA"), strict=True):
        _ = ax.text(
            x, 0.37, label, fontsize=9, weight="bold", ha="left" if x == columns[0] else "center"
        )
    authored = [c for c in document.cards if c.graph.model_id in REQUIRED_SPECIFICATION_NAMES]
    for index, card in enumerate(authored):
        y = 0.347 - index * 0.029
        _ = ax.plot((0.04, 0.97), (y + 0.013, y + 0.013), color=PALETTE["grid"], linewidth=0.7)
        _ = ax.text(columns[0], y, card.graph.model_id, fontsize=8.4, weight="bold")
        _ = ax.text(columns[0], y - 0.012, card.graph.execution, fontsize=7.8)
        for x, (_, shape) in zip(columns[1:5], card.graph.tensor_shapes, strict=True):
            _ = ax.text(x, y - 0.005, " x ".join(map(str, shape)), fontsize=8.6, ha="center")
        _ = ax.text(
            columns[5],
            y - 0.005,
            card.graph.source_sha256[:6],
            fontsize=7.8,
            ha="center",
        )
    _text(
        ax,
        0.04,
        0.105,
        """A: observation x state; B: next x previous x action. SHA: source-digest prefix only.
        Full tensors, settings, annotations, native graphs, dependency revisions and evidence
        digests are in the linked complete card.""",
        size=9.1,
        width=119,
    )
    _text(
        ax,
        0.04,
        0.047,
        """Scope: finite synthetic software models. These graphs do not establish human gratitude,
        contemplative realization, clinical efficacy or philosophical equivalence.""",
        size=9.2,
        width=118,
        bold=True,
    )
    return fig


def _companion(document: _Document, output: Path) -> str:
    sections: list[str] = []
    for card in document.cards:
        images = "".join(
            '<img alt="Native GNN declaration graph" src="data:image/png;base64,'
            + base64.b64encode((output / asset.path).read_bytes()).decode()
            + '">'
            for asset in card.native_assets
            if asset.path.endswith(".png")
        )
        declaration_path = graph_model_path(output, card.graph.model_id).relative_to(output)
        sections.append(
            "".join(
                (
                    f'<section id="{escape(card.graph.model_id)}">',
                    f"<h2>{escape(card.graph.model_id)}</h2>",
                    f"<p>{escape(card.graph.execution)}. ",
                    f'<a href="../{escape(card.graph.evidence_artifact)}">',
                    "Consumed evidence record</a>; ",
                    f'<a href="../{escape(str(declaration_path))}">',
                    "Exact declaration</a>.</p>",
                )
            )
            + "<details><summary>Native graph and complete admitted card</summary>"
            + images
            + '<pre tabindex="0" aria-label="Complete admitted model card; scroll for all tensors">'
            + escape(TypeAdapter(_Card).dump_json(card).decode())
            + "</pre></details></section>"
        )
    return "".join(
        (
            '<!doctype html><html lang="en"><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            "<title>GNN complete model cards</title><style>:root{color-scheme:light}",
            "body{background:#fff;color:#142e3a;max-width:1000px;margin:auto;",
            "padding:24px;font:17px/1.5 system-ui}a{color:#005c67}",
            "pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;",
            "max-width:100%;max-height:32rem;overflow:auto;box-sizing:border-box}",
            "details,section{min-width:0;max-width:100%}h2{overflow-wrap:anywhere}",
            "img{max-width:100%;height:auto}section{border-top:1px solid #a8b9c1;",
            "margin-top:32px}</style><h1>GNN complete model cards</h1>",
            "<p>Exact admitted declarations, tensors, scientific settings, native graph assets ",
            "and numerical consumer bindings. The declaration graph can contain cycles; ",
            "the time-unrolled Bayesian diagram explains POMDP tensor semantics. ",
            "Protocol carriers and local finite consumers do not become native GNN/pymdp ",
            "experiments by sharing a backend label.</p>",
            '<p><a href="../manuscript.html#sec-gnn-graphs">Manuscript model inventory</a> | ',
            '<a href="gnn-model-card.json">Machine-readable complete cards</a></p>',
            "<h2>Generator and dependency provenance</h2><pre>"
            + escape(
                record_json(
                    {
                        "schema": document.schema,
                        "catalog_sha256": document.catalog_sha256,
                        "parser_sha256": document.parser_sha256,
                        "renderer_sha256": document.renderer_sha256,
                        "generator_sha256": document.generator_sha256,
                        "dependencies": document.dependencies,
                    }
                )
            )
            + "</pre>"
            + "".join(sections)
            + "</html>",
        )
    )


def write_gnn_model_card(output: Path) -> AbstractArtifact:
    """Export page four plus complete machine-readable and accessible HTML model cards."""
    document = model_card_document(output)
    directory = output / "frontmatter"
    directory.mkdir(parents=True, exist_ok=True)
    paths = {suffix: directory / f"gnn-model-card.{suffix}" for suffix in ("pdf", "png", "svg")}
    fig = _draw(document)
    try:
        draw_canvas(fig.canvas)
        require_text_clearance(fig)
        texts = [t for t in fig.findobj(Text) if t.get_visible() and t.get_text()]
        for index, text in enumerate(texts):
            if any(
                text.get_window_extent().overlaps(other.get_window_extent())
                for other in texts[index + 1 :]
            ):
                message = f"GNN model-card text overlaps: {text.get_text()!r}"
                raise ContractError(message)
        export_frontmatter(fig, paths)
    finally:
        plt.close(fig)
    companion = directory / "gnn-model-card.html"
    _ = companion.write_text(_companion(document, output))
    _ = (directory / "gnn-model-card.json").write_text(
        TypeAdapter(_Document).dump_json(document).decode() + "\n"
    )
    artifact = _artifact(document, output)
    write_record(
        output / "reports/gnn_model_card.json",
        _Receipt(file_digest(directory / "gnn-model-card.json"), artifact, file_digest(companion)),
    )
    return artifact


def _artifact(document: _Document, output: Path) -> AbstractArtifact:
    paths = {
        suffix: output / "frontmatter" / f"gnn-model-card.{suffix}" for suffix in ("pdf", "png", "svg")
    }
    return AbstractArtifact(
        "modelcard",
        "GNN Bayesian graphical model and complete model cards",
        "".join(
            (
                f"Conditional Bayesian time slice and {len(document.cards)} admitted model consumers. ",
                "Complete dimensions, settings and provenance accompany the page.",
            )
        ),
        pdf=str(paths["pdf"].relative_to(output)),
        png=str(paths["png"].relative_to(output)),
        svg=str(paths["svg"].relative_to(output)),
        pdf_sha256=file_digest(paths["pdf"]),
        png_sha256=file_digest(paths["png"]),
        svg_sha256=file_digest(paths["svg"]),
        links=(
            ("Model inventory", "sec-gnn-graphs"),
            ("Methods", "sec-methods"),
            ("Limits", "sec-main-identification"),
            ("Complete cards", "frontmatter/gnn-model-card.html"),
        ),
    )


def gnn_model_card_valid(output: Path) -> bool:
    """Reject stale declarations, forged consumer metadata and missing or altered card products."""
    try:
        receipt = TypeAdapter(_Receipt).validate_json(
            (output / "reports/gnn_model_card.json").read_text()
        )
        document = model_card_document(output)
        return (
            receipt.document_sha256 == file_digest(output / "frontmatter/gnn-model-card.json")
            and receipt.artifact == _artifact(document, output)
            and TypeAdapter(_Document).validate_json(
                (output / "frontmatter/gnn-model-card.json").read_text()
            )
            == document
            and (output / "frontmatter/gnn-model-card.html").read_text() == _companion(document, output)
            and file_digest(output / "frontmatter/gnn-model-card.html") == receipt.companion_sha256
            and all(
                file_digest(output / path) == digest
                for path, digest in (
                    (receipt.artifact.pdf, receipt.artifact.pdf_sha256),
                    (receipt.artifact.png, receipt.artifact.png_sha256),
                    (receipt.artifact.svg, receipt.artifact.svg_sha256),
                )
            )
        )
    except (OSError, ValidationError, ContractError):
        return False
