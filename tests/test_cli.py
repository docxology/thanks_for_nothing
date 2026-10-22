# Copyright (c) 2026 Daniel Ari Friedman
"""Invoke the real CLI and its thin script entry points in child interpreters."""

import subprocess
import sys
from pathlib import Path

import pytest

from thanks_for_nothing.cli import validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "command",
    [
        ["-m", "thanks_for_nothing.cli", "--help"],
        [str(ROOT / "scripts/run_pipeline.py"), "--help"],
        [str(ROOT / "scripts/validate_project.py"), "--help"],
    ],
)
def test_cli_and_script_help_is_real_subprocess(command, tmp_path):
    result = subprocess.run(  # noqa: S603 - fixed local entry points
        [sys.executable, *command], cwd=tmp_path, text=True, capture_output=True, check=False
    )
    assert result.returncode == 0
    assert "Usage" in result.stdout


def test_cli_rejects_invalid_count_before_execution(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "thanks_for_nothing.cli", "run", "--replicates", "1"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Invalid value" in result.stderr
    assert not (tmp_path / "output").exists()


def test_validate_cli_accepts_actual_numerical_products(pipeline_case, capsys):
    validate(
        root=pipeline_case.root,
        output=pipeline_case.output,
        require_render=False,
        specification_dir=pipeline_case.specifications,
    )
    assert "Passed" in capsys.readouterr().out
    result = subprocess.run(  # noqa: S603 - fixed local CLI and explicit fixture roots
        [
            sys.executable,
            "-m",
            "thanks_for_nothing.cli",
            "validate",
            "--root",
            str(pipeline_case.root),
            "--output",
            str(pipeline_case.output),
            "--specification-dir",
            str(pipeline_case.specifications),
            "--no-require-render",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Passed" in result.stdout
