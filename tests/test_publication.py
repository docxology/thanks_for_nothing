# Copyright (c) 2026 Daniel Ari Friedman
"""Real cover rendering, identifier admission and numbered formalism controls."""

import re
import shutil
import subprocess
import unicodedata
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.formalisms import build_formalism_registry
from thanks_for_nothing.illustrations import build_illustration_registry
from thanks_for_nothing.publication import load_publication, valid_orcid, write_cover_header
from thanks_for_nothing.publication_checks import publication_valid
from thanks_for_nothing.reporting import render_manuscript

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("value", ["0000-0001-6232-9096", "0000-0002-1825-0097"])
def test_orcid_checksum(value):
    assert valid_orcid(value)
    assert not valid_orcid(value[:-1] + "0")
    assert not valid_orcid("invalid")


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("orcid", "0000-0001-6232-9090", "check digit"),
        ("doi-status", "assigned", "disagree"),
        ("doi", "10.1234/example", "disagree"),
        ("cover-image", "../escaped.png", "existing research-source"),
        ("pdf-footer-offset-mm", 2.5, "Footer offset"),
        ("pdf-body-font-pt", 12, "Footer offset"),
    ],
)
def test_metadata_rejects_invalid_identity(tmp_path, key, value, message):
    target = tmp_path / "docs/manuscript"
    shutil.copytree(ROOT / "docs/manuscript", target)
    metadata = yaml.safe_load((target / "metadata.yaml").read_text())
    metadata.update({"doi": None, "doi-status": "unassigned", "zenodo-draft": None})
    metadata[key] = value
    if key == "pdf-body-font-pt":
        metadata["pdf-footer-offset-mm"] = (value + 1) * 25.4 / 72
    (target / "metadata.yaml").write_text(yaml.safe_dump(metadata))
    with pytest.raises(ContractError, match=message):
        load_publication(tmp_path)


@pytest.mark.parametrize(
    "text",
    [
        "$$\nx=1\n$$",
        "$$\nx=1\\label{eq:a}\\tag{42}\n$$",
        "$$\nx=1\\label{eq:a}\\label{eq:b}\n$$",
        "$$\nx=1",
        "[unknown](#eq:missing)",
        "$$\nx=1\\label{eq:a}\n$$\n\n$$\ny=2\\label{eq:a}\n$$",
    ],
)
def test_formalism_registry_rejects_broken_sources(text):
    with pytest.raises(ContractError):
        build_formalism_registry(text)


@pytest.mark.parametrize(
    "text",
    [
        "![Caption](figure.png)",
        "Inline ![Caption](figure.png){#fig-inline}",
        "![Figure 2. Authored number](figure.png){#fig-manual}",
        "![Caption](figure.png){#fig-a}\n\n![Caption](other.png){#fig-a}",
        "[Missing](#fig-missing)",
    ],
)
def test_illustration_registry_rejects_broken_sources(text):
    with pytest.raises(ContractError):
        build_illustration_registry(text)


def test_assigned_identifier_tex_escaping_and_cover_tampering(tmp_path):
    target = tmp_path / "docs/manuscript"
    shutil.copytree(ROOT / "docs/manuscript", target)
    path = target / "metadata.yaml"
    metadata = yaml.safe_load(path.read_text())
    metadata.update({"doi": "10.1234/example", "doi-status": "assigned", "affiliation": "A & B_1"})
    path.write_text(yaml.safe_dump(metadata))
    assert load_publication(tmp_path).doi_display == "10.1234/example"
    tex = write_cover_header(tmp_path, tmp_path / "output").read_text()
    assert r"A \& B\_1" in tex
    assert r"\href{https://doi.org/10.1234/example}" in tex
    image = tmp_path / metadata["cover-image"]
    image.write_bytes(image.read_bytes() + b"tampered")
    with pytest.raises(ContractError, match="provenance"):
        load_publication(tmp_path)


def test_repository_metadata_rejects_non_https_github(tmp_path):
    target = tmp_path / "docs/manuscript"
    shutil.copytree(ROOT / "docs/manuscript", target)
    path = target / "metadata.yaml"
    path.write_text(
        path.read_text().replace(
            "https://github.com/docxology/thanks_for_nothing", "http://example.org/repo"
        )
    )
    with pytest.raises(ValidationError, match="repository-url"):
        load_publication(tmp_path)


def test_reserved_doi_requires_matching_unpublished_draft(tmp_path):
    target = tmp_path / "docs/manuscript"
    shutil.copytree(ROOT / "docs/manuscript", target)
    path = target / "metadata.yaml"
    metadata = yaml.safe_load(path.read_text())
    metadata.update({"doi": "10.5281/zenodo.12345", "doi-status": "reserved"})
    path.write_text(yaml.safe_dump(metadata))
    with pytest.raises(ContractError, match="bind its production"):
        load_publication(tmp_path)
    metadata["zenodo-draft"] = "https://zenodo.org/uploads/12345"
    path.write_text(yaml.safe_dump(metadata))
    assert load_publication(tmp_path).doi_display == (
        "10.5281/zenodo.12345 (reserved; unpublished draft)"
    )
    meta = load_publication(tmp_path)
    assert meta.doi_url == metadata["zenodo-draft"]
    header = write_cover_header(tmp_path, tmp_path / "output").read_text()
    assert "reserved; unpublished draft" in header
    assert r"\href{https://zenodo.org/uploads/12345}" in header
    assert "https://doi.org/10.5281/zenodo.12345" not in header


@pytest.mark.parametrize("reserved", [False, True])
def test_real_pdf_html_cover_and_document_order_numbering(tmp_path, reserved):
    root = tmp_path / "source"
    target = root / "docs/manuscript"
    shutil.copytree(ROOT / "docs/manuscript", target)
    metadata = yaml.safe_load((target / "metadata.yaml").read_text())
    metadata.update(
        {"doi": None, "doi-status": "unassigned", "zenodo-draft": None, "graphical-abstracts": False}
    )
    if reserved:
        metadata.update(
            {
                "doi": "10.5281/zenodo.12345",
                "doi-status": "reserved",
                "zenodo-draft": "https://zenodo.org/uploads/12345",
            }
        )
    (target / "metadata.yaml").write_text(yaml.safe_dump(metadata))
    source = tmp_path / "numbering.md"
    image = target / "assets/test.png"
    shutil.copyfile(target / "assets/emptiness-cover-v0.3.png", image)
    source.write_text(r"""# Test

See [later](#eq:first) and [earlier](#eq:second).

$$
\label{eq:second}
y=2
$$

$$
\label{eq:first}
x=1
$$

See [later figure](#fig-first) and [earlier figure](#fig-second).

![First in reading order.](docs/manuscript/assets/test.png){#fig-second width=50%}

![Second in reading order.](docs/manuscript/assets/test.png){#fig-first width=50%}
""")
    registry = build_formalism_registry(source.read_text())
    assert [(row.number, row.label) for row in registry.entries] == [(1, "eq:second"), (2, "eq:first")]
    _ = render_manuscript(root, tmp_path, source)
    html = (tmp_path / "manuscript.html").read_text()
    assert 'id="eq:second"' in html
    assert 'data-equation-number="1"' in html
    assert 'id="eq:first"' in html
    assert 'data-equation-number="2"' in html
    assert "Equation (1)" in html
    assert "Equation (2)" in html
    assert 'id="fig-second" data-figure-number="1"' in html
    assert 'id="fig-first" data-figure-number="2"' in html
    assert "Figure 1." in html
    assert "Figure 2." in html
    assert "0000-0001-6232-9096" in html
    expected = "10.5281/zenodo.12345" if reserved else "not assigned"
    assert expected in html
    assert ("reserved; unpublished draft" in html) == reserved
    if reserved:
        assert 'href="https://zenodo.org/uploads/12345"' in html
    result = subprocess.run(  # noqa: S603 - Fixed executable and real temporary PDF, without a shell.
        [shutil.which("pdftotext") or "pdftotext", str(tmp_path / "manuscript.pdf"), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Daniel Ari Friedman" in result.stdout
    assert "0000-0001-6232-9096" in result.stdout
    assert expected in result.stdout
    _assert_frontmatter(root, html, result.stdout)
    assert ("reserved; unpublished draft" in result.stdout) == reserved
    text = unicodedata.normalize("NFKC", result.stdout)
    assert re.search(r"y\s*=\s*2.*?\(1\)", text, re.DOTALL)
    assert re.search(r"x\s*=\s*1.*?\(2\)", text, re.DOTALL)
    assert re.search(r"Figure 1: First in reading order", text)
    assert re.search(r"Figure 2: Second in reading order", text)
    (tmp_path / "reports/manuscript.md").write_text(source.read_text())
    write_record(tmp_path / "reports/formalisms.json", registry)
    write_record(
        tmp_path / "reports/illustrations.json", build_illustration_registry(source.read_text())
    )
    assert publication_valid(root, tmp_path, require_render=True)
    _reject_render_mutations(root, tmp_path, html, reserved)
    write_record(tmp_path / "reports/formalisms.json", replace(registry, entries=()))
    assert not publication_valid(root, tmp_path, require_render=False)


def _assert_contents(html, text):
    pages = text.split("\f")
    assert "Contents" not in pages[0]
    assert "Contents" in pages[1]
    assert "Test" in pages[1]
    assert "See Equation" not in pages[1]
    assert "See Equation" in pages[2]
    assert html.index("</header>") < html.index('id="TOC"') < html.index("<main>")


def _assert_frontmatter(root, html, text):
    meta = load_publication(root)
    assert f'href="{meta.paper_license_url}"' in html
    assert meta.paper_license in " ".join(html.split())
    assert meta.paper_license in text
    assert meta.code_license in text
    assert meta.repository_url in text
    assert f'href="{meta.repository_url}"' in html
    _assert_contents(html, unicodedata.normalize("NFKC", text))


def _reject_render_mutations(root, output, html, reserved):
    swapped = html.replace('data-equation-number="1"', 'data-equation-number="pending"')
    swapped = swapped.replace('data-equation-number="2"', 'data-equation-number="1"')
    swapped = swapped.replace('data-equation-number="pending"', 'data-equation-number="2"')
    (output / "manuscript.html").write_text(swapped)
    assert not publication_valid(root, output, require_render=True)
    swapped_figures = html.replace('data-figure-number="1"', 'data-figure-number="pending"')
    swapped_figures = swapped_figures.replace('data-figure-number="2"', 'data-figure-number="1"')
    swapped_figures = swapped_figures.replace('data-figure-number="pending"', 'data-figure-number="2"')
    (output / "manuscript.html").write_text(swapped_figures)
    assert not publication_valid(root, output, require_render=True)
    for invalid in (
        re.sub(r'<nav id="TOC".*?</nav>', "", html, flags=re.DOTALL),
        re.sub(r'(<nav id="TOC"[^>]*>).*?(</nav>)', r"\1\2", html, flags=re.DOTALL),
        html.replace('href="#eq:first"', 'href="#eq:missing"'),
        html.replace("</main>", '<span id="eq:first"></span></main>'),
        html.replace("Figure 1.</strong>", "Figure 99.</strong>"),
        html.replace("https://orcid.org/0000-0001-6232-9096", "https://orcid.org/invalid"),
        html.replace("https://creativecommons.org/licenses/by/4.0/", "https://example.org/wrong"),
        html.replace("https://github.com/docxology/thanks_for_nothing", "https://example.org/wrong"),
    ):
        (output / "manuscript.html").write_text(invalid)
        assert not publication_valid(root, output, require_render=True)
    if reserved:
        wrong_link = html.replace("https://zenodo.org/uploads/12345", "https://zenodo.org/uploads/99999")
        (output / "manuscript.html").write_text(wrong_link)
        assert not publication_valid(root, output, require_render=True)
    (output / "manuscript.html").write_text(html.replace("Daniel Ari Friedman", "Incorrect Author"))
    assert not publication_valid(root, output, require_render=True)


@pytest.mark.parametrize(
    "source",
    [
        "$$\nx=1\n$$",
        "$$\nx=1\\label{eq:a}\\tag{42}\n$$",
        "$$\nx=1\\label{eq:a}\\label{eq:b}\n$$",
        "$$\nx=1\\label{eq:a}\n$$\n\n$$\ny=2\\label{eq:a}\n$$",
        "[unknown](#eq:missing)",
    ],
)
def test_real_lua_filter_fails_on_invalid_formalisms(source):
    result = subprocess.run(  # noqa: S603 - Fixed executable and authored filter, without a shell.
        [
            shutil.which("pandoc") or "pandoc",
            "--to=html",
            "--lua-filter",
            str(ROOT / "docs/manuscript/filters/formalisms.lua"),
        ],
        input=source,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
