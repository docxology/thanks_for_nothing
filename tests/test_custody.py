# Copyright (c) 2026 Daniel Ari Friedman
import shutil
from pathlib import Path

import pytest

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.custody import source_tree_receipt


@pytest.mark.parametrize(
    "input_path",
    [
        "src/model.py",
        "data/inspection.xml",
        "data/inspection.html",
        "data/inspection.pdf",
    ],
)
def test_receipt_binds_changed_source_but_ignores_generated_caches(tmp_path, input_path):
    original = Path(__file__).resolve().parents[1]
    shutil.copy(original / "pyproject.toml", tmp_path / "pyproject.toml")
    shutil.copy(original / "uv.lock", tmp_path / "uv.lock")
    source = tmp_path / "src"
    source.mkdir()
    shutil.copytree(original / "src/thanks_for_nothing", source / "thanks_for_nothing")
    path = tmp_path / input_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("precision = 4\n")
    before = source_tree_receipt(tmp_path)
    cache = source / "__pycache__"
    cache.mkdir()
    (cache / "model.pyc").write_bytes(b"generated")
    assert source_tree_receipt(tmp_path) == before
    path.write_text("precision = 8\n")
    after = source_tree_receipt(tmp_path)
    assert after.tree_sha256 != before.tree_sha256
    assert after.files != before.files


def test_different_executing_package_is_rejected(tmp_path):
    original = Path(__file__).resolve().parents[1]
    shutil.copy(original / "pyproject.toml", tmp_path / "pyproject.toml")
    shutil.copy(original / "uv.lock", tmp_path / "uv.lock")
    package = tmp_path / "src/thanks_for_nothing"
    shutil.copytree(original / "src/thanks_for_nothing", package)
    (package / "__init__.py").write_text('__version__ = "99.0.0"\n')
    with pytest.raises(ContractError, match="Executing package contents differ"):
        source_tree_receipt(tmp_path)


def test_missing_package_rejects_an_incomplete_source_root(tmp_path):
    with pytest.raises(ContractError, match="missing the package"):
        source_tree_receipt(tmp_path)
