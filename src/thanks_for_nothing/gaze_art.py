# Copyright (c) 2026 Daniel Ari Friedman
"""Admitted artwork and explicitly registered, unsmoothed model scanpaths."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Protocol

import numpy as np
from matplotlib.text import Text
from PIL import Image
from pydantic import BaseModel, ConfigDict

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_contracts import GazeDesign
from thanks_for_nothing.inference import FloatArray
from thanks_for_nothing.provenance import file_digest
from thanks_for_nothing.visual_style import PALETTE, PlotAxes


class _Artwork(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    sha256: str
    bytes: int
    dimensions_pixels: tuple[int, int]
    photo_credit: str
    license_url: str


class _CreditFigure(Protocol):
    def supxlabel(self, text: str, /, *, fontsize: float) -> Text: ...


def artwork_credit(fig: _CreditFigure, detail: str) -> None:
    """Keep source attribution and display modifications attached to every artwork figure."""
    _ = fig.supxlabel(
        f"Munch (1893); photo Nasjonalmuseet / Børre Høstland (CC BY 4.0).\n{detail}",
        fontsize=10,
    )


@dataclass(frozen=True, slots=True)
class ScenePath:
    """A sampled location sequence with its display title and background pixels."""

    title: str
    locations: tuple[int, ...]
    pixels: FloatArray


def copy_artwork(root: Path | None, output: Path) -> None:
    """Bind the unchanged acquired image and credit to the generated figure inventory."""
    packaged = Path(__file__).resolve().parent / "resources/artwork"
    source = (
        root / "data/artwork"
        if root is not None
        else packaged
        if packaged.is_dir()
        else Path(__file__).resolve().parents[2] / "data/artwork"
    )
    provenance = _Artwork.model_validate_json((source / "provenance.json").read_text())
    image = source / "scream-original.jpg"
    with Image.open(image) as original:
        dimensions = original.size
    if (
        file_digest(image) != provenance.sha256
        or image.stat().st_size != provenance.bytes
        or dimensions != provenance.dimensions_pixels
    ):
        message = "Scene artwork differs from its acquisition receipt"
        raise ContractError(message)
    target = output / "assets"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("scream-original.jpg", "provenance.json"):
        _ = shutil.copy2(source / name, target / name)


def artwork_pixels(output: Path) -> FloatArray:
    """Resample only for plotting; retain original file bytes and the whole painted frame."""
    with Image.open(output.parent / "assets/scream-original.jpg") as image:
        image.thumbnail((1200, 1600), Image.Resampling.LANCZOS)
        return np.asarray(image.convert("RGB"), dtype=np.float64) / 255


def draw_scanpath(axis: PlotAxes, design: GazeDesign, path: ScenePath) -> None:
    """Register unit-square coordinates to the full portrait, with straight sampled transitions."""
    aspect = len(path.pixels) / (path.pixels[:1].size / 3)
    _ = axis.imshow(path.pixels, extent=(0, 1, 0, aspect), aspect="equal")
    points = np.asarray(design.coordinates, dtype=np.float64)[
        list(path.locations[: design.trajectory_steps])
    ]
    x = points[:, :1].reshape(-1)
    y = points[:, 1:].reshape(-1) * aspect
    _ = axis.plot(x, y, "-", color=PALETTE["ink"], linewidth=3.5, alpha=0.85)
    _ = axis.plot(x, y, "o-", color=PALETTE["artwork_overlay"], linewidth=1.5, markersize=3)
    _ = axis.plot(x[:1], y[:1], "o", color=PALETTE["artwork_overlay"], markersize=7)
    _ = axis.plot(x[-1:], y[-1:], "s", color=PALETTE["artwork_overlay"], markersize=6)
    _ = axis.set(title=path.title)
    _ = axis.axis("off")
