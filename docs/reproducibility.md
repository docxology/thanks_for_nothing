# Reproduce and qualify the research

Run from the standalone Thanks for Nothing checkout. The [canonical command list](../AGENTS.md)
owns installation, pipeline, tests, validation and distribution build.
[Current facts](../output/reports/research_summary.md) provide executed quantities;
this guide specifies how to interpret the evidence.

## Portable setup and renderers

Use Python supported by [pyproject.toml](../pyproject.toml), uv and the frozen
lockfile. CI qualifies Python 3.11 and 3.14 separately. Install Pandoc 3.10.1 or
newer, XeLaTeX, TeX fonts and Poppler; the CI workflow records pinned Pandoc
acquisition and Linux system packages. Confirm tools execute with
`pandoc --version`, `xelatex --version` and `pdftoppm -v`.

```bash
uv sync --frozen --extra dev
uv run python scripts/acquire_external_inputs.py
uv run python scripts/restore_records.py
uv run python scripts/run_pipeline.py
uv run pytest tests/ --cov=thanks_for_nothing --cov-fail-under=90
uv run python scripts/validate_project.py
uv build
```

The default uv environment is a local `.venv`. Set `UV_PROJECT_ENVIRONMENT` for
an alternate location. Acquired notebooks and the accepted manuscript remain
local inputs; a source archive intentionally does not bundle them. The canonical
pipeline regenerates outputs and can take substantial time. Preserve the
distributed output directory before rebuilding when comparing an exact release.

## Author's local runtime and storage

The author's GitVault workflow keeps source, Python installation, virtual environment, outputs, temporary files
and task caches on the mounted GitVault volume. Bind `UV_PROJECT_ENVIRONMENT`,
`UV_PYTHON`, `UV_PYTHON_INSTALL_DIR`, `UV_CACHE_DIR`, `TMPDIR`,
`MPLCONFIGDIR` and notebook runtime/cache directories before source work.
Use `UV_LINK_MODE=copy` for cross-volume uv operations. Do not create an internal
replacement if the external volume is absent.

Verify both `sys.prefix` and `sys.base_prefix` after resolving paths; an external
environment can still refer to an internal base interpreter. Preserve the
declared Python version. Use uv rather than a bare pytest or pyenv shim.

The PDF surface requires actual Pandoc, XeLaTeX and Poppler execution. Notebook
execution requires the locked Jupyter stack. Invoke the tools, rather than
treating their presence on PATH as proof of operation.

## One complete numerical and publication chain

The pipeline copies and admits the GNN declarations, checks independent source
and dependency identities, runs reconstruction and corrected experiments, writes
typed records, draws the figure suite, composes the main text/captions/supplement,
renders PDF/HTML and executes the notebook companions. It then writes generated
documentation facts, reference closure, the complete artifact inventory and
validation report.

A partial run with rendering or notebook execution disabled is a development
scenario, not complete publication qualification. Use a separate output directory
to preserve prior or failed evidence. Keep source inputs fixed throughout a
qualifying run; the final source receipt must equal the initial one.

## Automated checks and meaningful failures

Run the full tests under both supported endpoint runtimes and enforce the
coverage floor in the canonical commands. Strict source checks cover production,
tests, scripts and typing overlays. New numerical tests use real files, fixed
seeds and mathematical examples; mocking frameworks do not replace dependencies.

Negative controls must reject malformed GNN inputs, broken pairing, forged
receipts, false exact identities, unknown tokens, unbound numerical literals,
incomplete captions, unindexed guides, missing local references and damaged
vector keys/colors. Real PDF tests distinguish requested margins and retain
portrait-caption/page-number clearance. Preserve failed logs and rerun the
affected scenario after correction.

Shared test infrastructure lives in `tests/support`, registered through
`tests/conftest.py`. The pipeline fixture owns a real admitted small-design run;
scientific fixtures own the small practice, gaze and scene/encoding studies;
model helpers copy and edit real GNN files. Test modules do not import other test
modules. This keeps fixture discovery independent of collection order while
preserving scientific assertions, seeds, cohort budgets and fixture scopes.
Run a single file with `uv run pytest tests/test_calibration.py` for a focused
method check, and use the complete coverage invocation in the canonical commands
for qualification. `--setup-plan` checks fixture resolution without claiming that
the expensive scientific fixture executed.

The Bernoulli availability oracle is checked against exhaustive original samples
and resampling sequences. Its admission rejects a forged exact probability. The
notebook timeout regression runs an actual slow cell under a shorter supplied
protocol budget and checks the retained failure log. Increasing that budget so
the cell completes makes the expected-failure assertion fail. These checks exercise
the failure boundaries rather than merely comparing parallel success flags.

## Inspect the actual outputs

Inspect every scientific PNG/SVG at publication size, every final PDF page, all
notebook image outputs and the actual HTML in normal and narrow viewports.
Check captions, legends, axis units, panel correspondence, tables, equation links,
image loading, cross-document links and page-edge clearance. Hash-bound browser
evidence describes the observed content and viewport, not native-device testing.

Original source notebooks remain unchanged; executed companions are separate
products. More simulated observations do not become human participants. Exact
replay applies to deterministic scientific records, not every platform-dependent
PDF metadata byte or native runtime-memory diagnostic.

## Requalify an editorial revision

Keep the previous PDF, reports and source receipt before regenerating the main
text. A prose-only change need not invent new numerical tests, but it changes
the declared source tree and can change pagination, citation placement and
internal destinations. Use the complete pipeline when scientific inputs or
execution change. For an editorial or graphical refresh over an admitted,
unchanged numerical bundle, use the publication-products rebuild described in
[manuscript production](manuscript-production.md#qualification-and-delivery).
Its receipt records retained numerical custody and whether companions were
reexecuted. Check documentation and manuscript-reference closure, and inspect
every final page. Source-level links must also resolve in the composed HTML; links to
supplemental figures and equations deserve particular attention.

Compare scientific records with the preceding qualified run separately from
source and artifact identities. Identical numerical records support continuity
of the computational results, while a new source hash identifies the editorial
revision. Do not reuse an old approval as approval of the new manuscript. Record
which checks were rerun, which earlier code-test evidence remains applicable,
and the exact revised products inspected. The
[reading guide](manuscript-reading-guide.md) provides routes for checking that
the linked evidence actually supports each expanded explanation.

## Installed distributions and independent review

Build a wheel and source distribution. Rebuild the wheel from the source archive
and compare members. Install into fresh external environments and run real
upstream API, numerical, rejecting-control and figure-export scenarios outside
the checkout. Source-tree imports do not qualify an installed package.

An independent reviewer must approve the exact frozen commit they did not build.
Preserve its source archive, file digests and executable classifications.
After authorized publication, verify remote main/tag identity and download
the release assets for byte/checksum comparison. Hosted CI is qualified only
when its actual jobs execute successfully; account budget or runner failures
remain separate from local qualification.

The [publication guide](manuscript-production.md) covers identity and numbering.
[Evidence ceilings](evidence-ceilings.md) distinguish software acceptance from
empirical claims. No successful command authorizes Zenodo upload or publication.
