# Copyright (c) 2026 Daniel Ari Friedman
"""Command-line research generation and fail-closed artifact validation."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.pipeline import run_pipeline
from thanks_for_nothing.validation import require_valid, validate_project

app = typer.Typer(
    no_args_is_help=True, help="Reproducible finite-model research on gratitude and absence."
)


@app.command()
def run(  # noqa: PLR0913 - CLI options are independent user-facing controls
    *,
    root: Annotated[Path | None, typer.Option(help="Repository source root")] = None,
    output: Annotated[Path | None, typer.Option(help="Artifact directory")] = None,
    replicates: Annotated[
        int | None, typer.Option(min=2, help="Override agents per stratum for a labeled development run")
    ] = None,
    render: Annotated[bool, typer.Option(help="Render manuscript formats")] = True,
    notebook: Annotated[bool, typer.Option(help="Execute companion notebook")] = True,
    specification_dir: Annotated[
        Path | None, typer.Option(help="Explicit GNN declaration directory")
    ] = None,
) -> None:
    """Generate the declared research artifacts and require every requested gate."""
    root = (root or Path.cwd()).resolve()
    destination = (output or root / "output").resolve()
    report = run_pipeline(
        root,
        destination,
        replicates=replicates,
        render=render,
        notebook=notebook,
        specification_dir=specification_dir,
    )
    Console().print(f"Passed {len(report.gates)} finite-model gates. Artifacts: {destination}")


@app.command()
def validate(
    *,
    root: Annotated[Path | None, typer.Option()] = None,
    output: Annotated[Path | None, typer.Option()] = None,
    require_render: Annotated[bool, typer.Option()] = True,
    specification_dir: Annotated[
        Path | None, typer.Option(help="Explicit GNN declaration directory")
    ] = None,
) -> None:
    """Recheck on-disk artifacts against their declarations and evidence contracts."""
    root = (root or Path.cwd()).resolve()
    destination = (output or root / "output").resolve()
    report = validate_project(
        root, destination, require_render=require_render, specification_dir=specification_dir
    )
    write_record(destination / "reports/validation.json", report)
    require_valid(report)
    Console().print(f"Passed {len(report.gates)} project gates.")


if __name__ == "__main__":
    app()
