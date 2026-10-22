# Copyright (c) 2026 Daniel Ari Friedman
"""Publication views of parsed GNN structure, distinct from empirical causal diagrams."""

from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.patches import Circle, FancyArrowPatch
from pydantic import TypeAdapter

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.figure_keys import draw_canvas
from thanks_for_nothing.gnn_graphs import GraphCatalog, ModelGraph
from thanks_for_nothing.visual_style import (
    PALETTE,
    PUBLICATION_FONT_POINTS,
    FigureRecord,
    PlotAxes,
    figure,
    save,
)


def _draw_graph(axis: PlotAxes, model: ModelGraph, *, node_margin_points: float = 18) -> None:
    names = tuple(name for name, _ in model.variables)
    neighbors = {name: set[str]() for name in names}
    for edge in model.edges:
        neighbors[edge.source].add(edge.target)
        neighbors[edge.target].add(edge.source)
    levels: dict[str, int] = {}
    while remaining := set(names) - levels.keys():
        root = max(sorted(remaining), key=lambda name: len(neighbors[name]))
        levels[root] = 0
        frontier = [root]
        while frontier:
            following: list[str] = []
            for name in frontier:
                for neighbor in sorted(neighbors[name] - levels.keys()):
                    levels[neighbor] = levels[name] + 1
                    following.append(neighbor)
            frontier = following
    layers = [
        [name for name in names if levels[name] == level] for level in range(max(levels.values()) + 1)
    ]
    positions = {
        name: ((index + 1) / (len(layer) + 1), 0.88 - 0.76 * level / max(1, len(layers) - 1))
        for level, layer in enumerate(layers)
        for index, name in enumerate(layer)
    }
    for edge in model.edges:
        arrow = FancyArrowPatch(
            positions[edge.source],
            positions[edge.target],
            arrowstyle="-|>" if edge.directed else "-",
            mutation_scale=15,
            shrinkA=node_margin_points,
            shrinkB=node_margin_points,
            linewidth=1.4,
            color=PALETTE["ink"],
            connectionstyle="arc3,rad=0.10",
        )
        arrow.set_gid(f"gnn_edge_{edge.source}_{edge.target}")
        _ = axis.add_patch(arrow)
    for name, position in positions.items():
        node = Circle(
            position,
            0.055,
            facecolor=PALETTE["artwork_overlay"],
            edgecolor=PALETTE["positive_recall"],
            linewidth=1.6,
        )
        node.set_gid(f"gnn_node_{name}")
        _ = axis.add_patch(node)
        _ = axis.text(*position, name, ha="center", va="center", fontsize=12, weight="bold")
    _ = axis.set(xlim=(0, 1), ylim=(0, 1))
    _ = axis.axis("off")


draw_declaration_graph = _draw_graph


def gnn_model_graph(output: Path) -> FigureRecord:
    """Render every distinct parsed topology, grouping only actually identical declarations."""
    catalog = TypeAdapter(GraphCatalog).validate_json(
        (output.parent / "data/gnn_graphs.json").read_text()
    )
    groups: dict[tuple[tuple[str, ...], tuple[tuple[str, str, bool], ...]], list[ModelGraph]] = {}
    for model in catalog.models:
        key = (
            tuple(name for name, _ in model.variables),
            tuple((e.source, e.target, e.directed) for e in model.edges),
        )
        groups.setdefault(key, []).append(model)
    fig, _ = figure(6.54, 4.5 * len(groups), automatic_layout=False)
    fig.clear()
    for index, models in enumerate(groups.values()):
        axis = fig.add_subplot(len(groups), 1, index + 1)
        axis.set_aspect("equal")
        _draw_graph(axis, models[0])
        _ = axis.set(title=f"Parsed topology / {len(models)} declarations")
    return save(
        fig,
        output,
        "gnn_model_graph",
        "GNN declaration dependencies",
        "Parsed nodes and directed edges; identical topologies are grouped, not inferred from data.",
        ("data/gnn_graphs.json",),
    )


def gnn_model_tensors(output: Path) -> FigureRecord:
    """Expose actual admitted dimensions and execution routes without duplicating scientific values."""
    catalog = TypeAdapter(GraphCatalog).validate_json(
        (output.parent / "data/gnn_graphs.json").read_text()
    )
    fig = _tensor_table(catalog)
    require_table_clearance(fig)
    return save(
        fig,
        output,
        "gnn_model_tensors",
        "Complete runtime GNN families",
        "Family/dimension rows group complete instances; R denotes restricted support.",
        ("data/gnn_graphs.json",),
    )


def require_table_clearance(fig: Figure) -> None:
    """Reject collisions between the actual rendered inventory labels and numeric columns."""
    draw_canvas(fig.canvas)
    labels = [text for axis in fig.axes for text in axis.texts if text.get_text()]
    for index, left in enumerate(labels):
        for right in labels[index + 1 :]:
            intersection = left.get_window_extent().intersection(
                left.get_window_extent(), right.get_window_extent()
            )
            if intersection is not None and intersection.width > 1 and intersection.height > 1:
                message = (
                    f"GNN tensor inventory text overlaps: {left.get_text()!r} / {right.get_text()!r}"
                )
                raise ContractError(message)


def _tensor_table(catalog: GraphCatalog) -> Figure:
    groups: dict[tuple[str, tuple[tuple[str, tuple[int, ...]], ...]], list[ModelGraph]] = {}
    for model in catalog.models:
        if not model.execution.startswith("Local / "):
            continue
        identity = model.execution.removeprefix("Local / ")
        groups.setdefault((identity, model.tensor_shapes), []).append(model)
    if not groups:
        message = "GNN tensor inventory requires complete runtime families"
        raise ContractError(message)
    fig, axis = figure(6.54, 0.41 * len(groups) + 1.5, automatic_layout=False)
    height = len(groups) + 2
    _ = axis.set(xlim=(0, 1), ylim=(0, height))
    _ = axis.axis("off")
    columns = (0.01, 0.47, 0.64, 0.82, 0.94)
    headers = ("Runtime family / instances", "A", "B", "C", "D")
    for x, label in zip(columns, headers, strict=True):
        _ = axis.text(
            x,
            height - 0.25,
            label,
            ha="left" if x == columns[0] else "center",
            va="top",
            fontsize=10.5,
            weight="bold",
        )
    for index, ((identity, _shapes), models) in enumerate(groups.items()):
        model = models[0]
        y = height - index - 1.25
        _ = axis.plot([0, 1], [y + 0.15] * 2, color=PALETTE["grid"], linewidth=0.7)
        label = identity.replace("_", " ").replace(" restricted", " (R)")
        _ = axis.text(columns[0], y, label, va="top", fontsize=10.5, weight="bold")
        role = (
            f"{len(models)} instance(s)" if model.execution.startswith("Local / ") else model.execution
        )
        _ = axis.text(columns[0], y - 0.40, role, va="top", fontsize=PUBLICATION_FONT_POINTS)
        for x, (_, shape) in zip(columns[1:], model.tensor_shapes, strict=True):
            _ = axis.text(
                x, y - 0.25, " x ".join(str(n) for n in shape), ha="center", va="top", fontsize=10.5
            )
    return fig
