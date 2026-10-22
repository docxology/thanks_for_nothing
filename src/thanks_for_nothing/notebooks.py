# Copyright (c) 2026 Daniel Ari Friedman
"""Execute the companion notebook with an explicitly bound interpreter."""

import os
import subprocess
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_design import load_gaze_task
from thanks_for_nothing.product_contracts import NOTEBOOK_NAMES, NotebookName
from thanks_for_nothing.visual_style import PALETTE


@dataclass(frozen=True, slots=True)
class _Kernel:
    argv: tuple[str, ...]
    display_name: str = "Thanks for Nothing"
    language: str = "python"


class _Output(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    output_type: str


class _Cell(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    cell_type: str
    execution_count: int | None = None
    outputs: tuple[_Output, ...] = ()


class _Notebook(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    cells: tuple[_Cell, ...]


@dataclass(frozen=True, slots=True)
class NotebookReceipt:
    """Observed execution counts from the actual produced notebook."""

    code_cells: int
    executed_cells: int
    error_outputs: int
    kernel_bound_to_current_interpreter: bool
    name: NotebookName = "gratitude_absence"


@dataclass(frozen=True, slots=True)
class NotebookContext:
    """Explicit run bindings; manual notebooks may use packaged declarations before a pipeline run."""

    root: Path
    output: Path
    specifications: Path


def notebook_context() -> NotebookContext:
    """Resolve injected run paths and reject an explicit output lacking preserved declarations."""
    selected_root = os.environ.get("TFN_NOTEBOOK_ROOT")
    root = (
        Path(selected_root).resolve()
        if selected_root
        else next(
            (p for p in (Path.cwd(), *Path.cwd().parents) if (p / "src/thanks_for_nothing").is_dir()),
            None,
        )
    )
    if root is None:
        message = "Run this companion from the repository or supply its execution context"
        raise ContractError(message)
    selected_output = os.environ.get("TFN_NOTEBOOK_OUTPUT")
    output = Path(selected_output).resolve() if selected_output else root / "output"
    specifications = output / "specifications"
    if not specifications.is_dir():
        if selected_output:
            message = "Selected notebook output lacks preserved GNN declarations"
            raise ContractError(message)
        specifications = Path(str(files("thanks_for_nothing").joinpath("models")))
    return NotebookContext(root, output, specifications)


def gaze_design_markdown(specifications: Path) -> str:
    """Display scene dimensions, policy membership and occupancy baselines from admission."""
    task = load_gaze_task(specifications)
    design = task.design
    sites = len(design.coordinates)
    baseline = ", ".join(f"{design.regions.count(r)}/{sites}" for r in range(len(design.channels)))
    policies = ", ".join(f"`{condition}`" for condition in design.conditions)
    excluded = ", ".join(
        str(i) for i in range(len(task.restricted_prior)) if task.restricted_prior[i] == 0
    )
    support = ", ".join(str(i) for i in range(len(task.open_prior)) if task.open_prior[i] > 0)
    return (
        f"**Admitted scene:** {len(design.transfer_state_map)}-by-{sites} transfer embedding; "
        f"risk over all {sites} locations; uniform-location regional baseline ({baseline}).\n\n"
        f"**Declared policies:** {len(design.conditions)} policies: {policies}.\n\n"
        f"**Structural support:** restricted prior excludes [{excluded}]; "
        f"open prior admits [{support}]."
    )


def _standalone_html(fragment: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thanks for Nothing: executable companion</title>
<style>
body {{ max-width: 54rem; margin: 2rem auto; padding: 0 1rem;
  color: {PALETTE["ink"]}; background: white; font: 17px/1.6 system-ui, sans-serif; }}
h1, h2, h3 {{ line-height: 1.25; }}
a {{ color: {PALETTE["positive_recall"]}; }}
.cell {{ margin: 1.8rem 0; }}
.prompt {{ color: {PALETTE["no_recall"]}; font-size: 0.85rem; }}
pre {{ padding: 1rem; border: 1px solid {PALETTE["grid"]}; overflow-x: auto;
  font-size: 0.85rem; line-height: 1.5; }}
code {{ font-family: ui-monospace, monospace; overflow-wrap: anywhere; }}
img {{ max-width: 100%; height: auto; }}
table {{ display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }}
td, th {{ padding: 0.4rem; border: 1px solid {PALETTE["grid"]}; }}
</style></head><body><main>{fragment}</main></body></html>
"""


def execute_notebook(
    root: Path,
    output: Path,
    *,
    name: NotebookName = "gratitude_absence",
    analysis: AnalysisDesign | None = None,
) -> NotebookReceipt:
    """Run all cells and export HTML using a temporary current-interpreter kernel."""
    target = output / "notebook"
    target.mkdir(parents=True, exist_ok=True)
    source = root / f"notebooks/{name}.ipynb"
    protocol = load_analysis() if analysis is None else analysis
    with TemporaryDirectory(prefix="tfn-kernel-") as directory:
        kernel_root = Path(directory)
        write_record(
            kernel_root / "kernels/tfn/kernel.json",
            _Kernel((sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}")),
        )
        environment = os.environ | {
            "TFN_NOTEBOOK_ROOT": str(root.resolve()),
            "TFN_NOTEBOOK_OUTPUT": str(output.resolve()),
            "JUPYTER_PATH": str(kernel_root),
            "JUPYTER_RUNTIME_DIR": str(kernel_root / "runtime"),
        }
        command = [
            sys.executable,
            "-m",
            "nbconvert",
            "--execute",
            "--to",
            "notebook",
            str(source),
            "--output",
            f"{name}.executed.ipynb",
            "--output-dir",
            str(target),
            "--ExecutePreprocessor.kernel_name=tfn",
            f"--ExecutePreprocessor.timeout={protocol.notebook_timeout_seconds}",
        ]
        executed = subprocess.run(  # noqa: S603 - fixed current interpreter and nbconvert arguments
            command, cwd=root, env=environment, check=False, text=True, capture_output=True
        )
        log = target / f"{name}.execution.log"
        _ = log.write_text(executed.stdout + executed.stderr)
        if executed.returncode:
            message = f"Notebook execution failed; see {log}"
            raise ContractError(message)
        html = subprocess.run(  # noqa: S603 - fixed current interpreter and nbconvert arguments
            [
                sys.executable,
                "-m",
                "nbconvert",
                "--to",
                "html",
                "--template",
                "basic",
                str(target / f"{name}.executed.ipynb"),
                "--output",
                f"{name}.html",
                "--output-dir",
                str(target),
            ],
            cwd=root,
            env=environment,
            check=False,
            text=True,
            capture_output=True,
        )
        _ = log.write_text(executed.stdout + executed.stderr + html.stdout + html.stderr)
        if html.returncode:
            message = f"Notebook HTML export failed; see {log}"
            raise ContractError(message)
        html_path = target / f"{name}.html"
        fragment = html_path.read_text().replace(
            'href="../docs/', 'href="' + os.path.relpath(root / "docs", target) + "/"
        )
        for companion in NOTEBOOK_NAMES:
            fragment = fragment.replace(
                f'href="{companion}.ipynb"', f'href="{companion}.executed.ipynb"'
            )
        _ = html_path.write_text(_standalone_html(fragment))
    notebook = _Notebook.model_validate_json((target / f"{name}.executed.ipynb").read_text())
    code = tuple(cell for cell in notebook.cells if cell.cell_type == "code")
    receipt = NotebookReceipt(
        len(code),
        sum(cell.execution_count is not None for cell in code),
        sum(o.output_type == "error" for c in code for o in c.outputs),
        kernel_bound_to_current_interpreter=True,
        name=name,
    )
    if not code or receipt.executed_cells != receipt.code_cells or receipt.error_outputs:
        msg = "Notebook did not execute every code cell without errors"
        raise ContractError(msg)
    return receipt
