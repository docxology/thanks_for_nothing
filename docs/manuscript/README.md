# Thanks for Nothing manuscript

The [main text](manuscript.md), [technical supplement](supplement.md),
[caption catalog](captions.yaml), and [bibliography](references.bib) are the
authoring sources. The [reading guide](../manuscript-reading-guide.md) maps each
question to its methods and complete evidence. The package's
[metadata](metadata.yaml), filters, templates, and cover provenance remain the
authority for the original production format. [Manuscript production](../manuscript-production.md)

## Render the retained edition

The published [combined archive](https://doi.org/10.5281/zenodo.23402517)
holds the original paper and code. The pinned reader build uses its retained
composition, compiled figures, graphical abstracts, and model card.
The staging script verifies the composed Markdown, authoring inputs, and
figure hashes against the native publication receipt. It adapts paths and
cross-reference syntax, then lays out the body and supplement as numbered
sections. Its numeric inventory checks parity with the sealed composition.
It is not a new numerical or human study.

Use uv, XeLaTeX, and a compatible Pandoc and pandoc-crossref pair. The reader
check used Pandoc 3.1.13 and pandoc-crossref 0.3.17.1. Prepare a clean working
checkout using the [pinned Template run guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md).
From this repository:

```sh
study_root=$(pwd)
git clone https://github.com/docxology/template.git ../template-render
cd ../template-render
git checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
uv sync --locked --no-dev --python 3.14
git -C "$study_root" worktree add --detach "$PWD/projects/working/thanks_for_nothing" HEAD

uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/thanks_for_nothing
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/thanks_for_nothing
```

The working checkout receives `output/pdf/thanks_for_nothing_combined.pdf`,
`output/web/index.html`, and validation and provenance reports under
`output/reports/`. The [reproduction guide](../reproducibility.md) separates
finite verification, historical source reconstruction, and full native production.
