# Copyright (c) 2026 Daniel Ari Friedman
"""Provenance for transcribed historical quantities and independent calibration descriptions."""

from math import fsum
from pathlib import Path
from typing import Annotated, ClassVar, Final, Literal
from zipfile import ZipFile

from numpy.lib.format import read_array_header_1_0, read_array_header_2_0, read_magic
from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing import calibration_fixtures
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_variables import ManuscriptVariable
from thanks_for_nothing.provenance import SOURCE_PINS, file_digest

Percent = Annotated[float, Field(ge=0, le=100, allow_inf_nan=False)]
PERCENTAGE_CLOSURE_TOLERANCE: Final = 1e-9
BASELINE_DIMENSIONS: Final = 4


class _Observations(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    schema_version: Literal["thanks_for_nothing.manuscript_observations.v1"]
    gratitude_source_sha256: str
    after_figure_locator: str = Field(min_length=1)
    after_positive_profile_percent: tuple[Percent, Percent, Percent]
    after_negative_profile_percent: tuple[Percent, Percent, Percent]
    after_status: Literal["transcribed_figure_only_no_executable_after_condition"]
    desteno_receipt: Literal["data/scholarship/receipts/v060/desteno2014.pdf"]
    desteno_receipt_sha256: str
    desteno_locator: str = Field(min_length=1)
    desteno_participants: int = Field(gt=0)


def historical_variables(root: Path) -> tuple[ManuscriptVariable, ...]:
    """Admit transcriptions against preserved primary-source bytes, never as simulated results."""
    relative = "data/sources/manuscript_observations.json"
    path = root / relative
    record = _Observations.model_validate_json(path.read_text())
    primary = next(pin for pin in SOURCE_PINS if pin.key == "fisher2025")
    if (
        record.gratitude_source_sha256 != primary.sha256
        or file_digest(root / primary.path) != primary.sha256
        or file_digest(root / record.desteno_receipt) != record.desteno_receipt_sha256
        or any(
            abs(fsum(values) - 100) > PERCENTAGE_CLOSURE_TOLERANCE
            for values in (record.after_positive_profile_percent, record.after_negative_profile_percent)
        )
    ):
        message = "Historical manuscript quantities lack their preserved source or percentage closure"
        raise ContractError(message)
    digest = file_digest(path)
    return tuple(
        ManuscriptVariable(name, value, f"source:{relative}", digest, selector)
        for name, value, selector in (
            (
                "SOURCE_AFTER_POSITIVE",
                "/".join(f"{v:g}" for v in record.after_positive_profile_percent),
                "/after_positive_profile_percent; " + record.after_figure_locator,
            ),
            (
                "SOURCE_AFTER_NEGATIVE",
                "/".join(f"{v:g}" for v in record.after_negative_profile_percent),
                "/after_negative_profile_percent; " + record.after_figure_locator,
            ),
            (
                "DESTENO_PARTICIPANTS",
                str(record.desteno_participants),
                "/desteno_participants; " + record.desteno_locator,
            ),
        )
    )


def calibration_variables() -> tuple[ManuscriptVariable, ...]:
    """Describe the actual independent known-answer generator without duplicating its constants."""
    fixtures = calibration_fixtures
    description = " ".join(
        (
            f"{len(fixtures.Fixture)} independent mathematical fixtures span a standard Gaussian null,",
            f"a +{fixtures.GAUSSIAN_SHIFT:g} SD Gaussian shift, a variance-standardized Student-t null",
            f"with {fixtures.HEAVY_TAIL_DF} degrees of freedom, a centered exponential null,",
            f"{len(fixtures.HETEROGENEOUS_SCALES)} zero-mean Gaussian strata with standard deviations",
            ", ".join(f"{v:g}" for v in fixtures.HETEROGENEOUS_SCALES)
            + f", and a centered Bernoulli({fixtures.BERNOULLI_PROBABILITY:g}) null.",
        )
    )
    return (
        ManuscriptVariable(
            "CALIBRATION_FIXTURE_SETTINGS",
            description,
            "package:calibration_fixtures.py",
            file_digest(Path(fixtures.__file__)),
            "Fixture; GAUSSIAN_SHIFT; HEAVY_TAIL_DF; HETEROGENEOUS_SCALES; BERNOULLI_PROBABILITY",
        ),
        ManuscriptVariable(
            "CALIBRATION_FIXTURES",
            str(len(fixtures.Fixture)),
            "package:calibration_fixtures.py",
            file_digest(Path(fixtures.__file__)),
            "count(Fixture)",
        ),
    )


def source_array_variables(output: Path) -> tuple[ManuscriptVariable, ...]:
    """Read original reconstruction dimensions from the preserved arrays, separately from corrected N."""
    relative = "data/source_reconstruction.npz"
    path = output / relative
    with ZipFile(path) as archive, archive.open("baseline.npy") as stream:
        version = read_magic(stream)
        reader = {(1, 0): read_array_header_1_0, (2, 0): read_array_header_2_0}.get(version)
        if reader is None:
            message = "Unsupported source reconstruction array version"
            raise ContractError(message)
        shape, _, dtype = reader(stream)
    if len(shape) != BASELINE_DIMENSIONS or any(size <= 0 for size in shape) or dtype.hasobject:
        message = "Source reconstruction requires a nonempty numeric baseline cohort"
        raise ContractError(message)
    agents = shape[0]
    return (
        ManuscriptVariable(
            "SOURCE_BELIEF_AGENTS", str(agents), relative, file_digest(path), "baseline.shape[0]"
        ),
    )
