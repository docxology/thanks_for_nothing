# Copyright (c) 2026 Daniel Ari Friedman
"""Exercise the generated native cover after moving the checkout."""

import shutil
import subprocess
from pathlib import Path

from thanks_for_nothing.publication import load_publication, write_cover_header

ROOT = Path(__file__).resolve().parents[1]


def test_generated_cover_survives_relocating_project_assets(tmp_path: Path) -> None:
    """Reuse the generated cover header in real XeLaTeX after moving its checkout."""
    root = tmp_path / "original checkout"
    manuscript = root / "docs/manuscript"
    manuscript.mkdir(parents=True)
    shutil.copy2(ROOT / "docs/manuscript/metadata.yaml", manuscript / "metadata.yaml")
    shutil.copytree(ROOT / "docs/manuscript/assets", manuscript / "assets")
    output = root / "output"
    panel = output / "frontmatter/panel with spaces.png"
    panel.parent.mkdir(parents=True)
    shutil.copy2(root / load_publication(root).cover_image, panel)
    header = write_cover_header(root, output, ((panel, (("Retained panel", "sec-panel"),)),))
    source = root / "fixture.md"
    source.write_text("# Portable reader {#sec-panel}\n\nAn ordinary paper section.\n")

    moved = root.rename(tmp_path / "moved checkout")
    pdf = moved / "output/manuscript.pdf"
    subprocess.run(  # noqa: S603 - fixed renderer and real test files, without a shell
        [
            shutil.which("pandoc") or "pandoc",
            str(moved / source.relative_to(root)),
            "--standalone",
            "--pdf-engine=xelatex",
            "--metadata-file",
            str(moved / "docs/manuscript/metadata.yaml"),
            "--resource-path",
            str(moved),
            "--include-in-header",
            str(moved / header.relative_to(root)),
            "--output",
            str(pdf),
        ],
        cwd=moved,
        capture_output=True,
        text=True,
        check=True,
    )
    rendered = subprocess.run(  # noqa: S603 - fixed executable and real PDF, without a shell
        [shutil.which("pdftotext") or "pdftotext", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Retained panel" in rendered.stdout
    assert "Portable reader" in rendered.stdout
