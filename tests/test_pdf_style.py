# Copyright (c) 2026 Daniel Ari Friedman
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from defusedxml import ElementTree
from PIL import Image

from thanks_for_nothing.publication import load_publication
from thanks_for_nothing.reporting import render_manuscript

ROOT = Path(__file__).resolve().parents[1]


def test_dense_body_retains_clearance_above_every_page_number(tmp_path):
    source = tmp_path / "dense-body.md"
    source.write_text(("Dense body marker with measured page geometry. " * 16 + "\n\n") * 40)

    render_manuscript(ROOT, tmp_path, source, graphical_abstracts=False)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and an actual PDF, no shell.
        [shutil.which("pdftotext") or "pdftotext", "-bbox", str(tmp_path / "manuscript.pdf"), "-"],
        capture_output=True,
        text=True,
        check=True,
    )

    namespace = {"x": "http://www.w3.org/1999/xhtml"}
    pages = ElementTree.fromstring(result.stdout).findall(".//x:page", namespace)
    assert len(pages) > 2
    for index, page in enumerate(pages[1:], 1):
        words = page.findall("x:word", namespace)
        footer = next(
            word
            for word in words
            if word.text == str(index) and float(word.attrib["yMin"]) > float(page.attrib["height"]) - 50
        )
        body_bottom = max(float(word.attrib["yMax"]) for word in words if word is not footer)
        assert float(footer.attrib["yMin"]) - body_bottom >= 2


@pytest.mark.parametrize("row_count", [4, 10, 90])
def test_table_keeps_compact_summaries_whole_and_long_tables_paginated(tmp_path, row_count):
    rows = [f"row{index:03d}" for index in range(row_count)]
    source = tmp_path / "compact-table.md"
    source.write_text(
        "Page-boundary control.\n\n"
        "\\vspace*{260mm}\n\n"
        "| Condition | Estimate |\n| --- | --- |\n"
        + "".join(f"| {row} | {index} |\n" for index, row in enumerate(rows))
    )

    render_manuscript(ROOT, tmp_path, source, graphical_abstracts=False)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and an actual PDF, no shell.
        [shutil.which("pdftotext") or "pdftotext", "-layout", str(tmp_path / "manuscript.pdf"), "-"],
        capture_output=True,
        text=True,
        check=True,
    )

    pages = result.stdout.split("\f")
    table_pages = [page for page in pages if "Condition" in page or rows[0] in page]
    if row_count <= 10:
        assert len(table_pages) == 1, "A compact table must not strand a header or split its rows"
    else:
        assert len(table_pages) > 1, "A long table must retain page breaks and repeated headers"
    assert all(row in "\n".join(table_pages) for row in rows)


def test_portrait_figure_and_caption_keep_physical_page_clearance(tmp_path):
    picture = tmp_path / "portrait.png"
    Image.new("RGB", (1308, 1874), "white").save(picture, dpi=(200, 200))
    source = tmp_path / "portrait.md"
    caption = (
        "A tall scientific figure with its complete explanatory caption. "
        "The panels describe declared computations and independent assessment targets. "
        "The key distinguishes estimates, intervals and exact controls. "
        "Every label retains the publication font size, and all caption text must remain "
        "inside the physical page with enough space for the page number. "
        "This regression exercises the actual PDF renderer with a portrait image."
    )
    source.write_text(f"# Portrait figure\n\n![{caption}]({picture}){{#fig-portrait width=100%}}\n")

    render_manuscript(ROOT, tmp_path, source, graphical_abstracts=False)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and an actual PDF, no shell.
        [shutil.which("pdftotext") or "pdftotext", "-bbox", str(tmp_path / "manuscript.pdf"), "-"],
        capture_output=True,
        text=True,
        check=True,
    )

    namespace = {"x": "http://www.w3.org/1999/xhtml"}
    pages = ElementTree.fromstring(result.stdout).findall(".//x:page", namespace)
    assert pages
    for page in pages:
        words = page.findall("x:word", namespace)
        assert all(float(word.attrib["yMax"]) <= float(page.attrib["height"]) - 10 for word in words)
    for index, page in enumerate(pages[1:], 1):
        words = page.findall("x:word", namespace)
        footer = next(
            word
            for word in words
            if word.text == str(index) and float(word.attrib["yMin"]) > float(page.attrib["height"]) - 50
        )
        body_bottom = max(float(word.attrib["yMax"]) for word in words if word is not footer)
        assert float(footer.attrib["yMin"]) - body_bottom >= 2
    assert "regression" in result.stdout
    assert "renderer" in result.stdout
    images = subprocess.run(  # noqa: S603 - Fixed Poppler executable and the same real PDF.
        [shutil.which("pdfimages") or "pdfimages", "-list", str(tmp_path / "manuscript.pdf")],
        capture_output=True,
        text=True,
        check=True,
    )
    portrait = next(
        fields
        for line in images.stdout.splitlines()
        if (fields := line.split())[3:5] == ["1308", "1874"]
    )
    assert abs(float(portrait[12]) - float(portrait[13])) <= 1, "Keep the image's aspect ratio"


@pytest.mark.parametrize("expected_margin_mm", [7, 9])
def test_real_pdf_has_red_links_metadata_margins_and_ten_point_body(tmp_path, expected_margin_mm):
    root = tmp_path / "source"
    shutil.copytree(ROOT / "docs/manuscript", root / "docs/manuscript")
    metadata_path = root / "docs/manuscript/metadata.yaml"
    metadata = yaml.safe_load(metadata_path.read_text())
    metadata["pdf-margin-mm"] = expected_margin_mm
    metadata_path.write_text(yaml.safe_dump(metadata))
    source = tmp_path / "style.md"
    source.write_text("""# Margin marker {#target}

An [external link](https://example.org) and an [internal link](#target).

The source citation is linked [@fisher2025].
""")
    render_manuscript(root, tmp_path, source, graphical_abstracts=False)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and a real rendered PDF, no shell.
        [
            shutil.which("pdftohtml") or "pdftohtml",
            "-xml",
            "-i",
            "-zoom",
            "1",
            "-stdout",
            str(tmp_path / "manuscript.pdf"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    tree = ElementTree.fromstring(result.stdout)
    red_fonts = {
        element.attrib["id"]
        for element in tree.iter("fontspec")
        if element.attrib.get("color", "").lower() == "#ff0000"
    }
    text_runs = [(element.attrib, "".join(element.itertext())) for element in tree.iter("text")]
    for phrase in ("external link", "internal link"):
        assert any(
            phrase in text and attributes["font"] in red_fonts for attributes, text in text_runs
        ), phrase
    page = next(
        page
        for page in tree.iter("page")
        if any("external link" in "".join(element.itertext()) for element in page.iter("text"))
    )
    left_edge = min(float(element.attrib["left"]) for element in page.iter("text"))
    margin_mm = 210 * left_edge / float(page.attrib["width"])
    assert expected_margin_mm - 0.3 <= margin_mm <= expected_margin_mm + 0.3
    footer = next(
        row for row in page.iter("text")
        if "".join(row.itertext()) == str(int(page.attrib["number"]) - 1)
    )
    assert float(footer.attrib["top"]) + float(footer.attrib["height"]) <= (
        float(page.attrib["height"]) - 10
    ), "Page numbers must retain 10 pt of clearance from the physical page edge"
    font_sizes = {
        element.attrib["id"]: float(element.attrib["size"]) for element in tree.iter("fontspec")
    }
    body_run = next(row for row in page.iter("text") if "external link" in "".join(row.itertext()))
    assert 9.5 <= font_sizes[body_run.attrib["font"]] <= 10.5
    reference_run = next(
        row for row in page.iter("text") if "Fisher, Elizabeth" in "".join(row.itertext())
    )
    assert 8.5 <= font_sizes[reference_run.attrib["font"]] <= 9.5
    link_runs = [
        element
        for element in tree.iter("text")
        if any(
            character.isalnum()
            for anchor in element.iter("a")
            for character in "".join(anchor.itertext())
        )
    ]
    assert link_runs
    assert all(element.attrib["font"] in red_fonts for element in link_runs)
    assert any("Fisher" in "".join(element.itertext()) for element in link_runs)


@pytest.mark.parametrize(
    ("prefix", "name", "date"),
    [
        ("An analytic robustness comparator", "Satterthwaite", "1946"),
        ("Sandved-Smith and colleagues' *There is no self-evidence*", "Sandved-Smith", "2026"),
    ],
)
def test_linked_citation_keeps_author_year_and_body_bounds(tmp_path, prefix, name, date):
    source = tmp_path / "citation-wrapping.md"
    paragraph = next(
        line
        for line in (ROOT / "docs/manuscript/supplement.md").read_text().splitlines()
        if line.startswith(prefix)
    )
    source.write_text(
        "# Citation wrapping\n\n" + paragraph + "\n\n\\newpage\n\n# References {.unnumbered}\n"
    )
    render_manuscript(ROOT, tmp_path, source, graphical_abstracts=False)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and a real rendered PDF, no shell.
        [
            shutil.which("pdftohtml") or "pdftohtml",
            "-xml",
            "-i",
            "-zoom",
            "1",
            "-stdout",
            str(tmp_path / "manuscript.pdf"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    pages = list(ElementTree.fromstring(result.stdout).iter("page"))
    page = next(
        page for page in pages
        if any(
            prefix.split("*")[0].split("'")[0].strip() in "".join(row.itertext())
            for row in page.iter("text")
        )
    )
    runs = list(page.iter("text"))
    linked = [row for row in runs if list(row.iter("a"))]
    author = next(row for row in linked if name in "".join(row.itertext()))
    year = next(row for row in linked if date in "".join(row.itertext()))
    assert author.attrib["top"] == year.attrib["top"]
    assert all(
        anchor.attrib["href"].endswith(f'#{pages[-1].attrib["number"]}')
        for anchor in author.iter("a")
    )
    glyphs = subprocess.run(  # noqa: S603 - Fixed Poppler executable and a real rendered PDF, no shell.
        [
            shutil.which("pdftotext") or "pdftotext",
            "-bbox",
            "-f",
            page.attrib["number"],
            "-l",
            page.attrib["number"],
            str(tmp_path / "manuscript.pdf"),
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    namespace = {"x": "http://www.w3.org/1999/xhtml"}
    body = ElementTree.fromstring(glyphs.stdout).find(".//x:page", namespace)
    assert body is not None
    margin = load_publication(ROOT).pdf_margin_mm
    body_right = float(body.attrib["width"]) * (1 - margin / 210) + 3
    assert all(float(word.attrib["xMax"]) <= body_right for word in body.findall("x:word", namespace)), (
        "Body glyphs must fit the margin with at most 3 pt of microtype punctuation protrusion"
    )


@pytest.mark.parametrize("location", ["body", "table"])
def test_long_primary_text_citations_fit_their_available_measure(tmp_path, location):
    main = (ROOT / "docs/manuscript/manuscript.md").read_text()
    supplement = (ROOT / "docs/manuscript/supplement.md").read_text()
    passage = next(line for line in main.splitlines() if line.startswith("The wording situates"))
    table = supplement.split("| Textual comparison |", 1)[1].split("\n\n", 1)[0]
    source = tmp_path / "long-primary-citations.md"
    source.write_text("# Citation measures\n\n" + (
        passage if location == "body" else "| Textual comparison |" + table
    ) + "\n\n\\newpage\n\n# References {.unnumbered}\n")
    render_manuscript(ROOT, tmp_path, source, graphical_abstracts=False)
    result = subprocess.run(  # noqa: S603 - Fixed Poppler executable and actual rendered primary-text fixtures.
        [shutil.which("pdftohtml") or "pdftohtml", "-xml", "-i", "-zoom", "1", "-stdout",
         str(tmp_path / "manuscript.pdf")],
        capture_output=True, text=True, check=True,
    )
    pages = list(ElementTree.fromstring(result.stdout).iter("page"))
    body = next(page for page in pages if any(
        ("The wording" if location == "body" else "Textual comparison") in "".join(row.itertext())
        for row in page.iter("text")
    ))
    if location == "body":
        right = float(body.attrib["width"]) * (1 - load_publication(ROOT).pdf_margin_mm / 210) + 3
        assert all(float(row.attrib["left"]) + float(row.attrib["width"]) <= right
                   for row in body.iter("text")), "A long title citation must fit the body margin"
    else:
        question = next(row for row in body.iter("text") if "Question" in "".join(row.itertext()))
        boundary, top = float(question.attrib["left"]), float(question.attrib["top"])
        citations = [row for row in body.iter("text") if list(row.iter("a"))
                     and float(row.attrib["left"]) < boundary and float(row.attrib["top"]) > top]
        assert citations, "Exercise actual linked citations in the first table column"
        assert all(float(row.attrib["left"]) + float(row.attrib["width"]) < boundary
                   for row in citations), "Citation text must not collide with the next column"
