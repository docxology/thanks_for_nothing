# src/ — the scientific logic

All analysis lives in `src/thanks_for_nothing/`. Scripts call it; nothing computes in a
script.

## Rules

- **Keep the three claims separate.** Source reconstruction, corrected computational
  experiments and the explicitly new conceptual model are different kinds of work. A
  simulation output supports a software or model claim; it does not establish human
  gratitude, contemplative insight, clinical benefit or philosophical equivalence.
- **Use the packaged GNN resources.** Import the pinned GNN and Realizing Emptiness
  distributions and use their real parser, admission and numerical APIs. Do not
  reimplement a parser locally or stub a distribution.
- **Keep mathematical controls independent of mutable model parameters**, so a control
  cannot move when a parameter changes.
- **Test real source edits, invalid probabilities, semantic nulls and exact replay** —
  the boundary modules (`boundary_*`) exist to make those states reachable.
- No mocks. Real files and numerical examples only.
