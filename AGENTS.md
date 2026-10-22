# Thanks for Nothing

Public research snapshot derived from template_code_project commit
04040a1e8eda0b31ce61db888cd1b3598f1696ca. Preserve licensed source preprints
unchanged. Acquire omitted notebooks locally using docs/external-inputs.md;
keep acquired originals and raw scholarship bodies outside version control.

The project separates source reconstruction, corrected computational experiments,
and an explicitly new conceptual model of gratitude for nothingness. Simulation
outputs support software and model claims. Human gratitude, contemplative insight,
clinical benefit and philosophical equivalence require separate evidence.

Model declarations live in packaged GNN resources. Import the pinned GNN and
Realizing Emptiness distributions; use their real parser, admission and numerical
APIs. Keep mathematical controls independent of mutable model parameters. Test
real source edits, invalid probabilities, semantic nulls and exact replay.

Use uv, real files and numerical examples; no mocks. Keep scientific logic in
src/thanks_for_nothing and scripts as thin orchestrators. Bind interpreter, venv,
UV_CACHE_DIR, TMPDIR and MPLCONFIGDIR to GitVault; verify prefix and base_prefix.
Preserve other workers' edits. Each worker owns explicit files; never revert
another owner. Root coordinates generated outputs and publication.

Canonical commands after environment setup:

```bash
uv sync --frozen --extra dev
uv run python scripts/acquire_external_inputs.py
uv run python scripts/restore_records.py
uv run python scripts/run_pipeline.py
uv run pytest tests/ --cov=thanks_for_nothing --cov-fail-under=90
uv run python scripts/validate_project.py
uv build
```

Render and inspect every final figure, notebook and manuscript PDF. Qualify the
installed wheel outside the checkout. An independent reviewer must approve code
they did not build before release. The author authorized the initial public
GitHub snapshot and combined Zenodo record on 2026-10-22. Future releases require
their own exact-candidate review and author authorization. See
docs/publication-handoff.md for archive contents and reciprocal identifiers.
