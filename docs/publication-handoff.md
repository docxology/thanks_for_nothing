# Public release and archive

The author authorized publication on 2026-10-22. Version 0.11.0 contains the
manuscript and one parentless public code snapshot. Earlier development commits,
tags, raw research downloads and original unlicensed notebooks remain outside
this public repository. Dated research dossiers describe their original scope;
their earlier draft-status statements are historical observations.

## Read and cite

- [Combined manuscript and code archive](https://doi.org/10.5281/zenodo.23402517).
- [GitHub repository](https://github.com/docxology/thanks_for_nothing).
- [Versioned release](https://github.com/docxology/thanks_for_nothing/releases/tag/v0.11.0).
- [Software citation metadata](../CITATION.cff).
- [Rendered manuscript](../output/manuscript.pdf).

The Zenodo description is the paper's complete two-paragraph abstract, extracted
from the generated manuscript rather than independently maintained.
The record describes a combined preprint and reproducibility package. Its
related identifiers include the GitHub release and exact snapshot commit.
The DOI identifies the combined package, not software alone.

## Contents and licenses

| Component | Contents and terms |
| --- | --- |
| Manuscript | PDF and authored text; original paper and figures CC BY 4.0 |
| Code snapshot | Original Python implementation, standalone GNN declarations, tests and documentation; MIT |
| Reproducibility artifacts | Numerical records, source bindings, figures, notebooks and model cards; see individual notices |
| Original preprints | Both exact licensed versions, unchanged and attributed under CC BY 4.0 |
| Dependencies and photograph | Separate licenses and attribution in [THIRD_PARTY.md](../THIRD_PARTY.md) |

The code ZIP contains the source, documentation and retained outputs. Zenodo and
the GitHub release also carry the manuscript separately, installable wheel,
source distribution and a manifest of file sizes and SHA256 digests. The manifest
records the root commit and release tag. Verify downloaded files against it.

Both original notebooks and the copied cell manifest are excluded because no
redistribution license was verified. Raw scholarly bodies and private task logs
are excluded. The [license audit](publication-license-audit-20261020.md) explains
the source-specific decisions; [external inputs](external-inputs.md) explains
local acquisition and digest verification. Dependency availability and the
original hosts remain external reproduction requirements.

## Reproduce and verify

Follow [external input setup](external-inputs.md) and
[reproducibility](reproducibility.md). Restore compressed records after a clean
checkout. Acquired originals remain ignored and are excluded from built
distributions. Scientific family/regime models are standalone GNN declarations;
per-agent fitted channels remain source-bound data under those declarations.

The release qualification runs from the exported source with its own source
receipt. Scientific outputs remain finite synthetic evidence; publication
does not establish human gratitude, contemplative realization or clinical
benefit. An independent reviewer must approve the frozen snapshot before
external publication. Hosted CI results are separate from local qualification.

## Publication custody

Private development history is preserved separately; the public repository is
initialized independently and receives exactly one root commit. No mirror push
or history rewrite is used. Manual Zenodo deposition archives the selected
manuscript and code together; automatic GitHub archiving must not create an
unrequested second software record.

The [original DOI reservation receipt](../data/publication/zenodo-draft.json)
is retained unchanged as historical evidence. Release metadata and the public
record supersede its draft-state observation. A build command never performs
publication. Subsequent releases require a new frozen package and author
authorization.
