# Copyright (c) 2026 Daniel Ari Friedman
"""The manuscript contract for situated main results and complete supplementary comparisons."""

import re
from pathlib import Path

from thanks_for_nothing.visual_tokens import MAIN_RESULT_FIGURES, SUPPLEMENT_ONLY_FIGURES


def _images(source: str) -> frozenset[str]:
    return frozenset(
        match.group(1)
        for match in re.finditer(r"!\[[\s\S]*?\]\(output/figures/([a-z0-9_]+)\.png\)", source)
    )


def figure_placement_valid(root: Path) -> bool:
    """Require the complete main-result situation set and keep detailed charts in the supplement."""
    main = (root / "docs/manuscript/manuscript.md").read_text()
    supplement = (root / "docs/manuscript/supplement.md").read_text()
    start = re.search(r"^# [^\n]*\{#sec-main-results\}[^\n]*\n", main, flags=re.MULTILINE)
    if start is None:
        return False
    results = main[start.end() :].split("\n# ", 1)[0]
    return (
        _images(results) == MAIN_RESULT_FIGURES
        and _images(main).isdisjoint(SUPPLEMENT_ONLY_FIGURES)
        and _images(supplement).issuperset(SUPPLEMENT_ONLY_FIGURES)
    )
