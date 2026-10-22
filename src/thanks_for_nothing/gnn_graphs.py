# Copyright (c) 2026 Daniel Ari Friedman
"""Bind actual GNN parser graphs and native renders to their numerical consumers."""

import inspect
import shutil
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar

import matplotlib as mpl
import numpy as np
from gnn.parsers.markdown_parser import MarkdownGNNParser
from gnn.visualization.graph import network_visualizations
from PIL import Image
from pydantic import BaseModel, ConfigDict, JsonValue, TypeAdapter

from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.product_contracts import REQUIRED_SPECIFICATION_NAMES
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.specifications import load_model
from thanks_for_nothing.standalone_gnn import GenerativeCatalog, read_generative_catalog


class _Variable(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    name: str
    dimensions: tuple[int, ...]
    var_type: str


class _Connection(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    source_variables: tuple[str, ...]
    target_variables: tuple[str, ...]
    connection_type: str


class _Parsed(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    variables: tuple[_Variable, ...]
    connections: tuple[_Connection, ...]


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """One parsed declaration edge; cycles do not imply an instantaneous causal DAG."""

    source: str
    target: str
    directed: bool


@dataclass(frozen=True, slots=True)
class ModelGraph:
    """Graph, tensor dimensions and the exact record consuming this declaration."""

    model_id: str
    source_sha256: str
    variables: tuple[tuple[str, tuple[int, ...]], ...]
    edges: tuple[GraphEdge, ...]
    tensor_shapes: tuple[tuple[str, tuple[int, ...]], ...]
    execution: str
    evidence_artifact: str
    evidence_sha256: str


@dataclass(frozen=True, slots=True)
class GraphAsset:
    """A native renderer output whose bytes and source-derived content are checked."""

    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class GraphCatalog:
    """Deterministic graph evidence without volatile parser UUIDs or timestamps."""

    schema: str
    parser_sha256: str
    renderer_sha256: str
    models: tuple[ModelGraph, ...]
    assets: tuple[GraphAsset, ...]


def _payload(path: Path) -> dict[str, JsonValue]:
    return deepcopy(_parsed_payload(path.read_text()))


@lru_cache(maxsize=128)
def _parsed_payload(source: str) -> dict[str, JsonValue]:
    result = MarkdownGNNParser().parse_string(source)
    if not result.success or result.errors or result.warnings:
        message = "GNN graph parse failed for the supplied source bytes"
        raise ContractError(message)
    return result.model.to_dict()


def describe_model(output: Path, bundle: ResearchBundle, name: str) -> ModelGraph:
    """Read topology and dimensions from the same admitted bytes as the computation."""
    path = graph_model_path(output, name)
    model = load_model(name, path.parent)
    parsed = _Parsed.model_validate(_payload(path))
    bindings = {
        "gratitude": (bundle.study.model_sha256, "study", "Finite learner"),
        "nothingness": (bundle.nothingness.model_sha256, "nothingness", "Finite comparators"),
        "emptiness_practice": (bundle.practice.model_sha256, "emptiness_practice", "Finite inquiry"),
        "gaze": (bundle.gaze.model_sha256, "gaze", "Finite scene inquiry"),
        "boundary_gaze": (bundle.boundary_gaze.model_sha256, "boundary_gaze", "Finite joint inquiry"),
        **{
            row.condition: (row.model_sha256, "attention", "Native GNN / pymdp")
            for row in bundle.attention.rows
        },
    }
    if name not in REQUIRED_SPECIFICATION_NAMES:
        generative = TypeAdapter(GenerativeCatalog).validate_json(
            (output / "data/generative_models.json").read_text()
        )
        entry = next(m for m in generative.models if m.model_id == name)
        expected, record, execution = entry.source_sha256, "generative_models", f"Local / {entry.family}"
    elif name == "analysis":
        stored = TypeAdapter(type(load_analysis(output / "specifications"))).validate_json(
            (output / "data/analysis_protocol.json").read_text()
        )
        if stored != load_analysis(output / "specifications"):
            message = "GNN analysis declaration differs from its consumed protocol"
            raise ContractError(message)
        expected, record, execution = model.source_hash, "analysis_protocol", "Protocol carrier"
    else:
        expected, record, execution = bindings[name]
    if expected != model.source_hash:
        message = f"GNN graph differs from executed model: {name}"
        raise ContractError(message)
    variables = tuple((v.name, v.dimensions) for v in parsed.variables)
    names = {v.name for v in parsed.variables}
    edges = tuple(
        GraphEdge(source, target, c.connection_type == "directed")
        for c in parsed.connections
        for source in c.source_variables
        for target in c.target_variables
    )
    if any(e.source not in names or e.target not in names for e in edges):
        message = f"GNN graph contains an undeclared endpoint: {name}"
        raise ContractError(message)
    shapes = tuple(
        (key, np.asarray(value, dtype=np.float64).shape)
        for key, value in (
            ("A", model.tensors.A),
            ("B", model.tensors.B),
            ("C", model.tensors.C),
            ("D", model.tensors.D),
        )
    )
    if any(dict(variables).get(key) != shape for key, shape in shapes):
        message = f"GNN graph dimensions differ from admitted tensors: {name}"
        raise ContractError(message)
    artifact = f"data/{record}.json"
    return ModelGraph(
        name,
        model.source_hash,
        variables,
        edges,
        shapes,
        execution,
        artifact,
        file_digest(output / artifact),
    )


def graph_model_path(output: Path, name: str) -> Path:
    """Resolve authored GNN inputs and executable instances through their explicit namespaces."""
    directory = output / "specifications"
    if name not in REQUIRED_SPECIFICATION_NAMES:
        directory /= "instances"
    return directory / f"{name}.gnn.md"


def expected_graphs(output: Path, bundle: ResearchBundle) -> tuple[ModelGraph, ...]:
    """Require complete generative coverage before admitting every graph and numerical binding."""
    generative = read_generative_catalog(output)
    names = (*REQUIRED_SPECIFICATION_NAMES, *(m.model_id for m in generative.models))
    return tuple(describe_model(output, bundle, name) for name in names)


def write_gnn_graphs(output: Path, bundle: ResearchBundle) -> GraphCatalog:
    """Run the pinned GNN renderer and reject missing native network products."""
    models = expected_graphs(output, bundle)
    assets: list[GraphAsset] = []
    for model in models:
        directory = output / "gnn" / model.model_id
        directory.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="render-", dir=directory.parent) as temporary:
            stage = Path(temporary)
            for source in _native_render(output, model, stage):
                path = directory / source.name
                _ = shutil.copyfile(source, path)
                assets.append(GraphAsset(str(path.relative_to(output)), file_digest(path)))
    catalog = GraphCatalog(
        "thanks_for_nothing.gnn_graphs.v1",
        file_digest(Path(inspect.getfile(MarkdownGNNParser))),
        file_digest(Path(inspect.getfile(network_visualizations))),
        models,
        tuple(assets),
    )
    write_record(output / "data/gnn_graphs.json", catalog)
    if not gnn_graphs_valid(output, bundle):
        message = "Native GNN graph products failed topology or source admission"
        raise ContractError(message)
    return catalog


def _native_render(output: Path, model: ModelGraph, stage: Path) -> tuple[Path, Path]:
    original_style = mpl.rcParams.copy()
    mpl.rcdefaults()
    try:
        rendered = network_visualizations.generate_network_visualizations(
            _payload(graph_model_path(output, model.model_id)), stage, model.model_id
        )
    finally:
        mpl.rcParams.update(original_style)
    paths = tuple(stage / f"{model.model_id}_{s}" for s in ("network_graph.png", "network_stats.json"))
    for path in paths:
        if str(path) not in rendered or not path.is_file() or not path.stat().st_size:
            message = f"GNN renderer did not produce a required graph product: {path.name}"
            raise ContractError(message)
    return paths[0], paths[1]


def _native_content_valid(output: Path, model: ModelGraph) -> bool:
    directory = output / "gnn" / model.model_id
    stats = TypeAdapter(dict[str, JsonValue]).validate_json(
        (directory / f"{model.model_id}_network_stats.json").read_text()
    )
    edges = tuple(e for e in model.edges if e.source != e.target)
    if (
        stats.get("total_variables") != len(model.variables)
        or stats.get("connection_types") != dict(Counter(f"{e.source}->{e.target}" for e in edges))
        or stats.get("gnn_edge_orientation")
        != {
            "directed_variable_pairs": sum(e.directed for e in edges),
            "undirected_variable_pairs": sum(not e.directed for e in edges),
        }
    ):
        return False
    with TemporaryDirectory(prefix="admit-", dir=directory.parent) as temporary:
        image, replay_stats = _native_render(output, model, Path(temporary))
        if stats != TypeAdapter(dict[str, JsonValue]).validate_json(replay_stats.read_text()):
            return False
        with (
            Image.open(image) as fresh,
            Image.open(directory / f"{model.model_id}_network_graph.png") as retained,
        ):
            return fresh.size == retained.size and np.array_equal(
                np.asarray(fresh.convert("RGBA")), np.asarray(retained.convert("RGBA"))
            )


def gnn_graphs_valid(output: Path, bundle: ResearchBundle) -> bool:
    """Replay native rendering to reject stale sources, forged statistics or substituted pixels."""
    try:
        return _gnn_graphs_valid(output, bundle)
    except (OSError, ValueError):
        return False


def _gnn_graphs_valid(output: Path, bundle: ResearchBundle) -> bool:
    catalog = TypeAdapter(GraphCatalog).validate_json((output / "data/gnn_graphs.json").read_text())
    expected = expected_graphs(output, bundle)
    paths = {
        f"gnn/{m.model_id}/{m.model_id}_{suffix}"
        for m in expected
        for suffix in ("network_graph.png", "network_stats.json")
    }
    if (
        catalog.schema != "thanks_for_nothing.gnn_graphs.v1"
        or catalog.models != expected
        or {a.path for a in catalog.assets} != paths
        or len(catalog.assets) != len(paths)
        or catalog.parser_sha256 != file_digest(Path(inspect.getfile(MarkdownGNNParser)))
        or catalog.renderer_sha256 != file_digest(Path(inspect.getfile(network_visualizations)))
    ):
        return False
    for asset in catalog.assets:
        path = output / asset.path
        if not path.resolve().is_relative_to(output.resolve()) or not path.is_file():
            return False
        if file_digest(path) != asset.sha256:
            return False
    return all(_native_content_valid(output, model) for model in expected)
