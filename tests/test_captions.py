# Copyright (c) 2026 Daniel Ari Friedman
from pathlib import Path
from shutil import copytree

import pytest
import yaml
from pydantic import ValidationError

from thanks_for_nothing.bundle import read_bundle
from thanks_for_nothing.captions import captions_complete
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.manuscript_composition import compose_source

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("defect", ["none", "field", "whitespace", "duplicate", "unknown", "number"])
def test_complete_caption_authoring_and_numerical_admission(tmp_path, defect):
    docs = tmp_path / "docs/manuscript"
    copytree(ROOT / "docs/manuscript", docs)
    path = docs / "captions.yaml"
    catalog = yaml.safe_load(path.read_text())
    if defect == "field":
        catalog["captions"][0].pop("scope")
    elif defect == "whitespace":
        catalog["captions"][0]["task"] = "   "
    elif defect == "duplicate":
        catalog["captions"].append(catalog["captions"][0])
    elif defect == "number":
        next(c for c in catalog["captions"] if c["figure"] == "recall_situation")["task"] = (
            "There were 1280 independent experimental units."
        )
    path.write_text(yaml.safe_dump(catalog, allow_unicode=True))
    token = "{{CAPTION_ABSENT}}" if defect == "unknown" else "{{CAPTION_RECALL_SITUATION}}"
    (docs / "manuscript.md").write_text(
        f"![{token}](output/figures/recall_situation.png){{#fig-recall width=100%}}"
    )
    if defect == "none":
        bundle = read_bundle(ROOT / "output")
        text, ledger = compose_source(tmp_path, ROOT / "output", bundle, {})
        level = 100 * bundle.statistics.contrasts[0].estimate.confidence
        assert f"pointwise analytic {level:g}%" in text
        assert f"{bundle.study.design.replicates} independent paired units" in text
        assert "docs/manuscript/captions.yaml" in {row.path for row in ledger.templates}
    else:
        with pytest.raises((ValidationError, ContractError)):
            compose_source(tmp_path, ROOT / "output", read_bundle(ROOT / "output"), {})


def test_caption_inventory_rejects_a_missing_scientific_figure(tmp_path):
    docs = tmp_path / "docs/manuscript"
    copytree(ROOT / "docs/manuscript", docs)
    assert captions_complete(tmp_path)
    path = docs / "supplement.md"
    path.write_text(path.read_text().replace("{{CAPTION_PAIRED_SPREAD}}", "A hand-written caption."))
    assert not captions_complete(tmp_path)
