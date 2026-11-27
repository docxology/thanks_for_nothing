# output/ — generated artifacts

The [full pipeline](../scripts/run_pipeline.py) generates research records, figures,
reports, specifications, executed notebooks and the manuscript readers.
The [record restore script](../scripts/restore_records.py) restores admitted
archive records. The [retained publication rebuild](../docs/manuscript-production.md#qualification-and-delivery)
regenerates reader-facing products from those records. These files record what
each route produced.

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
