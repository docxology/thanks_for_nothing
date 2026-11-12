# data/ — sources, receipts and custody records

Inputs and evidence records: `sources/` (the preserved upstream notebook and paper),
`scholarship/receipts/` (one record per cited work, plus the parsed bibliography),
`provenance/`, `artwork/`, `publication/` and `claim_contract.json`.

## Rules

- **Sources are preserved and digest-recorded.** `data/sources/` holds the upstream
  notebook and paper as received. Record their digests before interpreting them; never
  edit a source to fit the model.
- **One receipt per citation.** A scholarship receipt names the work and what was taken
  from it. Do not cite a work that has no receipt, and do not widen a receipt's claim
  beyond what the source supports.
- **Provenance files describe where a byte came from**, not what it means. Keep them
  accurate when an input is replaced.
- **Do not deposit.** `publication/` holds drafts only; no Zenodo deposition or DOI
  assignment is authorized by this project.
- **Distinguish what would falsify a claim from what would merely be convincing**
  (`claim_contract.json`) when adding an input.
