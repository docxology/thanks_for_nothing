# tests/ — real files, no mocks

The suite covers artifacts, custody, calibration, captions, the CLI, documentation and
the boundary experiments.

## Rules

- **No mocks.** Validate against real files and numerical examples. A mock cannot fail
  the way the real GNN parser or distribution does.
- **Test the failure states the boundary exists for**: real source edits, invalid
  probabilities, semantic nulls and exact replay.
- **Custody is tested.** Source notebooks and papers under `data/sources` have digests;
  a test that changes a source without updating its digest should fail.
- **Generated outputs are rebuilt**, so a test comparing prose to a number should read
  the generated value rather than a copied constant.
- Passing tests are verification, not independent review of the work.
