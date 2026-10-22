# Copyright (c) 2026 Daniel Ari Friedman
"""Bind task dimensions, structural supports and attribution to their actual records."""

from hashlib import sha256
from pathlib import Path
from typing import ClassVar

import numpy as np
from pydantic import BaseModel, ConfigDict

from thanks_for_nothing.artifacts import record_json
from thanks_for_nothing.boundary_design import load_boundary_task
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_variables import ManuscriptVariable
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.specifications import load_model


class ArtworkAttribution(BaseModel):
    """Attribution fields from the acquired artwork's immutable provenance."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    artist: str
    title: str
    date: int
    accession: str
    photo_credit: str
    reproduction_license_on_commons: str

    @property
    def text(self) -> str:
        """Render the verified credit without a parallel handwritten caption."""
        return (
            f"{self.artist}, {self.title} ({self.date}), {self.accession}; photograph "
            f"{self.photo_credit}; {self.reproduction_license_on_commons}"
        )


def additional_variables(
    output: Path, bundle: ResearchBundle, used: set[str]
) -> tuple[ManuscriptVariable, ...]:
    """Generate only requested additional values, including minimal-source compositions."""
    values: list[ManuscriptVariable] = []
    boundary = bundle.boundary_gaze
    digest = sha256(record_json(boundary).encode()).hexdigest()
    count = len(boundary.design.scene_maps)
    for name, value, selector in (
        ("BOUNDARY_ALTERNATIVE_RESPONSES", str(count - 1), "count(design.scene_maps) - 1"),
        (
            "BOUNDARY_QUERIES",
            str(len(bundle.gaze.design.coordinates) + len(boundary.design.probe_costs)),
            "count(gaze.design.coordinates) + count(design.probe_costs)",
        ),
        (
            "BOUNDARY_ENCODING_LABELS",
            ", ".join(f"H{i}" for i in range(count)),
            "indices(design.scene_maps)",
        ),
    ):
        if name in used:
            values.append(ManuscriptVariable(name, value, "data/boundary_gaze.json", digest, selector))
    values.extend(_record_dimensions(bundle, used))
    values.extend(_recall_dimensions(output, bundle, used))
    if used & {"MODEL_BOUNDARY_RESTRICTED_PRIOR", "MODEL_BOUNDARY_EXCLUDED_ENCODINGS"}:
        task = load_boundary_task(output / "specifications")
        if task.model.source_hash != boundary.model_sha256:
            message = "Boundary tensor declarations differ from the executed experiment"
            raise ContractError(message)
        prior = task.gaze.restricted_prior
        probabilities = tuple(
            float(np.sum(prior[i : i + 1], dtype=np.float64)) for i in range(len(prior))
        )
        for name, value, selector in (
            (
                "MODEL_BOUNDARY_RESTRICTED_PRIOR",
                ", ".join(f"{v:g}" for v in probabilities),
                "native restricted_prior",
            ),
            (
                "MODEL_BOUNDARY_EXCLUDED_ENCODINGS",
                ", ".join(f"H{i}" for i, probability in enumerate(probabilities) if probability == 0),
                "indices(native restricted_prior == 0)",
            ),
        ):
            if name in used:
                values.append(
                    ManuscriptVariable(
                        name,
                        value,
                        "specifications/emptiness_practice.gnn.md",
                        task.gaze.structural_hash,
                        selector,
                    )
                )
    if "ARTWORK_CREDIT" in used:
        path = output / "assets/provenance.json"
        credit = ArtworkAttribution.model_validate_json(path.read_text())
        values.append(
            ManuscriptVariable(
                "ARTWORK_CREDIT",
                credit.text,
                "assets/provenance.json",
                file_digest(path),
                "artist/title/date/accession/photo_credit/reproduction_license_on_commons",
            )
        )
    if "EXACT_PROCESS_PROBABILITIES" in used:
        path = output / "data/exact_decision.json"
        values.append(
            ManuscriptVariable(
                "EXACT_PROCESS_PROBABILITIES",
                ", ".join(
                    f"{row.process_probability:g}" for row in bundle.exact_decision.operating_points
                ),
                "data/exact_decision.json",
                file_digest(path),
                "operating_points[].process_probability",
            )
        )
    return tuple(values)


def _recall_dimensions(
    output: Path, bundle: ResearchBundle, used: set[str]
) -> tuple[ManuscriptVariable, ...]:
    if not used & {"MODEL_RECALL_STATES", "MODEL_RECALL_OBSERVATIONS"}:
        return ()
    model = load_model("gratitude", output / "specifications")
    if model.source_hash != bundle.study.model_sha256:
        message = "Recall tensor declarations differ from the executed experiment"
        raise ContractError(message)
    return tuple(
        ManuscriptVariable(
            name, str(value), "specifications/gratitude.gnn.md", model.source_hash, selector
        )
        for name, value, selector in (
            ("MODEL_RECALL_STATES", len(model.tensors.D), "count(admitted tensors.D)"),
            ("MODEL_RECALL_OBSERVATIONS", len(model.tensors.A), "count(admitted tensors.A)"),
        )
        if name in used
    )


def _record_dimensions(bundle: ResearchBundle, used: set[str]) -> tuple[ManuscriptVariable, ...]:
    records = (
        (
            "MODEL_ATTENTION_LOCATIONS",
            len(bundle.attention.rows[0].beliefs[0]),
            "data/attention.json",
            record_json(bundle.attention),
            "count(rows[0].beliefs[0])",
        ),
        (
            "GAZE_CANDIDATES",
            len(bundle.gaze.design.channels[0][0]),
            "data/gaze.json",
            record_json(bundle.gaze),
            "count(design.channels[0][0])",
        ),
        (
            "GAZE_REGION_COUNT",
            len(bundle.gaze.design.channels),
            "data/gaze.json",
            record_json(bundle.gaze),
            "count(design.channels)",
        ),
        (
            "UPSTREAM_PRACTICE_COUNT",
            len(bundle.upstream_practice.protocol_ids),
            "data/upstream_practice.json",
            record_json(bundle.upstream_practice),
            "count(protocol_ids)",
        ),
    )
    return tuple(
        ManuscriptVariable(name, str(value), source, sha256(raw.encode()).hexdigest(), selector)
        for name, value, source, raw, selector in records
        if name in used
    )
