# External inputs and public payload

The public snapshot includes the exact Fisher et al. preprint DOCX and
Sandved-Smith et al. preprint PDF unchanged, with CC BY 4.0 attribution in
[THIRD_PARTY.md](../THIRD_PARTY.md). Original code is MIT; the new manuscript and
figures are CC BY 4.0. Dependency and photograph licenses remain separate.

The original Colab notebooks have no verified redistribution license. They and
the copied `source_line` extracts in the private cell manifest are omitted.
Raw scholarship downloads are also omitted unless individually cleared.
The [catalogue](../data/scholarship/sources.json), bibliography, primary-source
links and digest pins remain. Historical research dossiers describe reading in
the private development checkout; they do not mean the public package contains
those downloaded bodies. The public export supplies a digest inventory of omitted
receipts under `publication/omitted-receipts.json`, not replacement reading receipts.
Historic raw-body paths are provenance locators, not bundled resources.

Full reconstruction, manuscript composition and tests require three separately
acquired inputs: the two original notebooks and DeSteno et al.'s accepted
manuscript, which anchors a historical participant-count transcription. Obtain
them directly from their original hosts for your local research use:

```bash
uv sync --frozen --extra dev
uv run python scripts/acquire_external_inputs.py
uv run python scripts/restore_records.py
uv run pytest tests/ --cov=thanks_for_nothing --cov-fail-under=90
uv run python scripts/run_pipeline.py
```

The [acquisition inventory](../configs/external-inputs.json) declares exact URLs,
destinations and SHA256 values. The command reuses exact existing files, refuses
to replace mismatches, fails on host/download errors, and verifies downloaded
bytes before exposing the destination. It grants no redistribution permission.
No missing source is replaced by a simplified implementation or invented result.
CI acquires these files transiently, without caching or uploading them.

Large generated JSON records are carried as gzip files in the public snapshot to
fit GitHub's file-size limit. The restore command verifies compressed and expanded
SHA256 values, reuses exact files, and refuses to replace changed local records.
`configs/retained-records.json` is generated from the frozen numerical artifacts;
compression changes storage only. Run restoration once after a clean checkout,
before tests or replay of retained results. A full pipeline run can also regenerate
the numerical records. The private development checkout already has expanded records.

An installed wheel deliberately omits the notebooks. Source-dependent APIs accept
an explicit `root` pointing to a hydrated source checkout. Calls without those
inputs fail with acquisition guidance. New finite-model APIs continue to use
the installed model resources. Wheels and source distributions exclude the
notebooks, private cell manifest and raw scholarship bodies even after local
acquisition. Do not use `git add -f` to defeat the input exclusions.

For offline research, transfer the three exact inputs into the declared local
paths from a copy you may lawfully access; run the acquisition command to verify
existing hashes without downloading. If original hosts change bytes or withdraw
access, retain the failure and resolve custody before proceeding. An artifact
from the previous run does not establish that a fresh reconstruction succeeded.
