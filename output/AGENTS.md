# output/ — generated artifacts

Everything here is produced by `scripts/run_pipeline.py` (assets, data, figures, reports,
specifications, `notebook/`, `manuscript.html`, `manuscript.pdf`). It is the system of
record only for what a run produced, never for what a claim means.

## Rules

- **Do not edit by hand.** Regenerate from inputs. An output corrected in place will be
  overwritten by the next run or, worse, will agree with prose and disagree with the code.
- **Root coordinates publication from here**; a worker who owns a specific file should not
  rewrite another's output.
- **Render and inspect every final figure, notebook and manuscript PDF** before release.
  An unopened artifact is an unchecked claim.
- **Qualify the installed wheel outside the checkout**; passing tests inside the tree are
  not a qualification of the distribution.
- Keep this directory free of credentials and private runtime state.
