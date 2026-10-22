# Copyright (c) 2026 Daniel Ari Friedman
from pathlib import Path

import pytest

from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_composition import compose_source

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "literal",
    [
        "There were 1280 independent agents.",
        "Whiskers show 95% confidence intervals.",
        r"The question likelihood is $1/3$.",
        "There were 2 paired samples.",
        "The process probability was .85.",
        "The observed effect was 7e-4.",
        "There were `1280` independent agents.",
        r"The excluded encoding was $H=2$.",
    ],
)
def test_unbound_experimental_literals_are_rejected(tmp_path, literal):
    docs = tmp_path / "docs/manuscript"
    docs.mkdir(parents=True)
    (docs / "manuscript.md").write_text("{{AGENTS}} independent units. " + literal)
    with pytest.raises(ContractError, match="Unbound numerical literal"):
        compose_source(tmp_path, ROOT / "output", read_bundle(ROOT / "output"), {})


def test_definitions_citations_and_textual_locators_remain_authored(tmp_path):
    docs = tmp_path / "docs/manuscript"
    docs.mkdir(parents=True)
    (docs / "manuscript.md").write_text(
        r"A probability satisfies $0\leq p\leq1$ and Brier uses $(q-y)^2$. "
        "The editions are SN 12.15 and MN 121 [@thanissaro1997, pp. 1-2]. "
        "The executed cohort contains {{AGENTS}} units."
    )
    bundle = read_bundle(ROOT / "output")
    text, _ = compose_source(tmp_path, ROOT / "output", bundle, {})
    assert "SN 12.15" in text
    assert f"{len({row.paired_id for row in bundle.study.rows})} units" in text
