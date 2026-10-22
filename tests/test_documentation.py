# Copyright (c) 2026 Daniel Ari Friedman
import pytest

from thanks_for_nothing.documentation import documentation_audit


@pytest.mark.parametrize("defect", ["none", "file", "anchor", "unindexed", "escape", "index"])
def test_real_markdown_links_and_discoverability(tmp_path, defect):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Docs\n\n[Guide](guide.md#purpose)\n")
    (docs / "guide.md").write_text("# Purpose\n\n[Back](README.md)\n")
    if defect == "file":
        (docs / "README.md").write_text("[Guide](absent.md)")
    elif defect == "anchor":
        (docs / "README.md").write_text("[Guide](guide.md#absent)")
    elif defect == "unindexed":
        (docs / "orphan.md").write_text("# Undiscoverable guide")
    elif defect == "escape":
        (docs / "guide.md").write_text("[Outside](../../outside.md)")
    elif defect == "index":
        (docs / "README.md").rename(docs / "former-index.md")
    report = documentation_audit(tmp_path)
    assert report.all_pass == (defect == "none")
    assert bool(report.issues) == (defect != "none")
    assert all(row.sha256 for row in report.inputs)


def test_examples_are_not_confused_with_live_documentation_targets(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text(
        "# Docs\n\n```markdown\n[Example](not-a-real-file.md)\n```\n\n"
        "[External](https://example.org/does-not-exist)\n"
    )
    assert documentation_audit(tmp_path).all_pass


def test_composed_manuscript_fragments_resolve_across_components(tmp_path):
    docs = tmp_path / "docs/manuscript"
    docs.mkdir(parents=True)
    (docs.parent / "README.md").write_text("# Docs")
    (docs / "manuscript.md").write_text("[Technical target](#eq:target)")
    (docs / "supplement.md").write_text(r"$$q=1\label{eq:target}$$")
    assert documentation_audit(tmp_path).all_pass


def test_partial_run_records_omitted_rendered_products_but_checks_other_outputs(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text(
        "[PDF](../output/manuscript.pdf)\n[HTML](../output/manuscript.html)\n"
        "[Data](../output/data.json)\n"
    )
    products = tmp_path / "products"
    products.mkdir()
    (products / "data.json").write_text("{}")
    partial = documentation_audit(tmp_path, output=products, include_rendered=False)
    assert partial.all_pass
    assert partial.excluded_products == ("manuscript.html", "manuscript.pdf")
    full = documentation_audit(tmp_path, output=products)
    assert not full.all_pass
    assert full.excluded_products == ()
    assert {row.target for row in full.issues} == {
        "../output/manuscript.pdf",
        "../output/manuscript.html",
    }
    (products / "data.json").rename(products / "absent.json")
    broken_partial = documentation_audit(tmp_path, output=products, include_rendered=False)
    assert not broken_partial.all_pass
    assert broken_partial.issues[0].target == "../output/data.json"
