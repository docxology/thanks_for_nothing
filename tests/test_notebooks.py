# Copyright (c) 2026 Daniel Ari Friedman
"""Real nbconvert subprocess checks with an interpreter-bound temporary kernel."""

import json
import sys
from pathlib import Path

import pytest

from tests.support.models import change_gaze_settings, copy_models, edit_model
from thanks_for_nothing.analysis_design import AnalysisDesign, load_analysis
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gaze_design import load_gaze_task
from thanks_for_nothing.notebooks import execute_notebook


def _source(root, code):
    path = root / "notebooks/gratitude_absence.ipynb"
    path.parent.mkdir(parents=True)
    cells = [{"cell_type": "markdown", "id": "intro", "metadata": {}, "source": ["# Test"]}]
    if code is not None:
        cells.append(
            {
                "cell_type": "code",
                "id": "compute",
                "metadata": {},
                "source": [code],
                "execution_count": None,
                "outputs": [],
            }
        )
    path.write_text(json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells}))


def test_actual_notebook_executes_current_interpreter_and_exports_html(tmp_path):
    _source(tmp_path, f"import sys\nassert sys.executable == {sys.executable!r}\nprint('kernel-bound')")
    output = tmp_path / "output"
    receipt = execute_notebook(tmp_path, output)
    assert receipt.code_cells == receipt.executed_cells == 1
    assert receipt.error_outputs == 0
    assert receipt.kernel_bound_to_current_interpreter
    html = (output / "notebook/gratitude_absence.html").read_text()
    assert "kernel-bound" in html
    assert html.startswith("<!doctype html>")
    assert "<script" not in html
    assert (output / "notebook/gratitude_absence.execution.log").stat().st_size > 40


def test_actual_failing_cell_records_output_and_rejects(tmp_path):
    _source(tmp_path, "raise ValueError('deliberate-negative-control')")
    output = tmp_path / "output"
    with pytest.raises(ContractError, match="Notebook execution failed"):
        execute_notebook(tmp_path, output)
    assert (
        "deliberate-negative-control"
        in (output / "notebook/gratitude_absence.execution.log").read_text()
    )


def test_notebook_consumes_selected_output_and_preserved_settings(tmp_path):
    output = tmp_path / "selected-run"
    models = output / "specifications"
    models.mkdir(parents=True)
    copy_models(models)
    edit_model(models, "analysis", notebook_replicates=3)
    _source(
        tmp_path,
        "from thanks_for_nothing.notebooks import notebook_context\n"
        "from thanks_for_nothing.analysis_design import load_analysis\n"
        "context = notebook_context()\n"
        f"assert str(context.output) == {str(output.resolve())!r}\n"
        "assert load_analysis(context.specifications).notebook_replicates == 3\n"
        "print('selected-run-bound')",
    )
    receipt = execute_notebook(tmp_path, output)
    assert receipt.error_outputs == 0
    assert "selected-run-bound" in (output / "notebook/gratitude_absence.html").read_text()


def test_explicit_notebook_output_without_models_is_rejected(tmp_path):
    _source(tmp_path, "from thanks_for_nothing.notebooks import notebook_context\nnotebook_context()")
    output = tmp_path / "unbound-run"
    with pytest.raises(ContractError, match="Notebook execution failed"):
        execute_notebook(tmp_path, output)
    assert "lacks preserved GNN" in (output / "notebook/gratitude_absence.execution.log").read_text()


def test_gaze_exported_prose_follows_changed_real_declaration(tmp_path):
    output = tmp_path / "selected-run"
    models = output / "specifications"
    models.mkdir(parents=True)
    copy_models(models)
    design = load_gaze_task(models).design
    change_gaze_settings(
        models,
        {
            "coordinates": list(design.coordinates[:4]),
            "regions": [0, 1, 2, 0],
            "transfer_state_map": [list(row[:4]) for row in design.transfer_state_map],
            "initial_location": 0,
            "conditions": [c for c in design.conditions if c != "uniform_open"],
            "comparisons": [pair for pair in design.comparisons if "uniform_open" not in pair],
        },
    )
    _source(
        tmp_path,
        "from IPython.display import Markdown, display\n"
        "from thanks_for_nothing.notebooks import notebook_context\n"
        "context = notebook_context()",
    )
    path = tmp_path / "notebooks/gratitude_absence.ipynb"
    excerpt = json.loads(path.read_text())
    original = json.loads(
        (Path(__file__).resolve().parents[1] / "notebooks/gaze_emptiness.ipynb").read_text()
    )
    excerpt["cells"].extend(
        c
        for c in original["cells"]
        if c["id"]
        in {"gaze-design-summary", "gaze-emptiness-06", "gaze-emptiness-10", "gaze-emptiness-12"}
    )
    path.write_text(json.dumps(excerpt))
    receipt = execute_notebook(tmp_path, output)
    assert receipt.error_outputs == 0
    html = (output / "notebook/gratitude_absence.html").read_text()
    for stale in ("2-by-13", "all 13 locations", "5/13, 5/13, 3/13", "Six policies"):
        assert stale not in html
    for derived in ("2-by-4", "all 4 locations", "2/4, 1/4, 1/4", "5 policies"):
        assert derived in html


def test_gaze_export_rejects_fixed_weight_prose_under_unequal_embedding(tmp_path):
    output = tmp_path / "selected-run"
    models = output / "specifications"
    models.mkdir(parents=True)
    copy_models(models)
    design = load_gaze_task(models).design
    weights = [list(row) for row in design.transfer_state_map]
    for site, region in enumerate(design.regions):
        if region == 2:
            weights[0][site], weights[1][site] = 0.25, 0.75
    change_gaze_settings(models, {"transfer_state_map": weights})
    _source(
        tmp_path,
        "from IPython.display import Markdown, display\n"
        "from thanks_for_nothing.notebooks import notebook_context\n"
        "from thanks_for_nothing.gaze_design import load_gaze_task\n"
        "context = notebook_context()\n"
        "design = load_gaze_task(context.specifications).design\n"
        "neutral = next(i for i, region in enumerate(design.regions) if region == 2)\n"
        "print('Actual neutral weights:', [row[neutral] for row in design.transfer_state_map])",
    )
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / "notebooks/gratitude_absence.ipynb"
    excerpt = json.loads(path.read_text())
    original = json.loads((root / "notebooks/gaze_emptiness.ipynb").read_text())
    excerpt["cells"].extend(
        c for c in original["cells"] if c["id"] in {"gaze-design-summary", "gaze-emptiness-06"}
    )
    path.write_text(json.dumps(excerpt))
    receipt = execute_notebook(tmp_path, output)
    assert receipt.code_cells == receipt.executed_cells == 2
    assert receipt.error_outputs == 0
    html = (output / "notebook/gratitude_absence.html").read_text()
    assert "Actual neutral weights: [0.25, 0.75]" in html
    assert "equal mixture" not in html
    assert "equal mixture" not in (root / "docs/manuscript/supplement.md").read_text()


def test_empty_notebook_is_not_vacuous_success(tmp_path):
    _source(tmp_path, None)
    with pytest.raises(ContractError, match="every code cell"):
        execute_notebook(tmp_path, tmp_path / "output")


def test_actual_concept_figure_cells_prepare_their_temporary_sources(tmp_path):
    original = json.loads(
        (Path(__file__).resolve().parents[1] / "notebooks/gratitude_absence.ipynb").read_text()
    )
    cells = [
        cell for cell in original["cells"] if cell["id"] in {"visualize", "enacted-mechanism-figure"}
    ]
    assert len(cells) == 2
    _source(
        tmp_path,
        "from thanks_for_nothing.nothingness import build_nothingness_audit\n"
        "from thanks_for_nothing.emptiness_practice import build_practice_audit\n"
        "from thanks_for_nothing.upstream_practice import build_upstream_practice_audit\n"
        "absence = build_nothingness_audit()\n"
        "practice = build_practice_audit(replicates=2)\n"
        "upstream = build_upstream_practice_audit()\n",
    )
    path = tmp_path / "notebooks/gratitude_absence.ipynb"
    actual = json.loads(path.read_text())
    actual["cells"].extend(cells)
    path.write_text(json.dumps(actual))
    output = tmp_path / "output"
    receipt = execute_notebook(tmp_path, output)
    assert receipt.code_cells == receipt.executed_cells == 3
    assert receipt.error_outputs == 0
    executed = json.loads((output / "notebook/gratitude_absence.executed.ipynb").read_text())
    assert (
        sum(
            "image/png" in result.get("data", {})
            for cell in executed["cells"]
            for result in cell.get("outputs", [])
        )
        == 2
    )


def test_supplied_notebook_timeout_rejects_slow_cell_and_records_failure(tmp_path):
    # Given a real cell that outlasts the explicitly selected execution budget.
    _source(tmp_path, "import time\ntime.sleep(3)")
    analysis = AnalysisDesign.model_validate(
        load_analysis().model_dump() | {"notebook_timeout_seconds": 1}
    )
    output = tmp_path / "output"

    # When nbconvert executes with the supplied analysis protocol.
    with pytest.raises(ContractError, match="Notebook execution failed"):
        execute_notebook(tmp_path, output, analysis=analysis)

    # Then its persisted subprocess log identifies the actual timeout failure.
    log = (output / "notebook/gratitude_absence.execution.log").read_text()
    assert "CellTimeoutError" in log
    assert "timed out" in log
