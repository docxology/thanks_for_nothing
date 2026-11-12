# scripts/ — two thin orchestrators

`run_pipeline.py` and `validate_project.py` only. No analysis belongs here.

## Rules

- **Thin wrappers.** Read inputs, call `src/thanks_for_nothing/`, write outputs. If a
  script starts deciding something, move the decision into `src/` and test it.
- **Bind the environment to GitVault.** Use `uv`; set the interpreter, venv,
  `UV_CACHE_DIR`, `TMPDIR` and `MPLCONFIGDIR` on the mounted vault, and verify `prefix`
  and `base_prefix` before a run.
- **Regenerate outputs from inputs**, never edit an output to agree with prose.
- Do not add network calls or credentials; a run must be reproducible from local inputs.
- Preserve other workers' edits: each worker owns explicit files and no script should
  rewrite another owner's output.
