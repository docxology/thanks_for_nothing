# notebooks/ — four worked examples

`belief_updating.ipynb`, `boundary_gaze.ipynb`, `gaze_emptiness.ipynb` and
`gratitude_absence.ipynb` show the model in use. They are demonstrations, not the
system of record.

## Rules

- **The upstream source notebook is preserved, not edited.** Source material lives under
  `data/sources` with its digest recorded; a notebook here may reproduce or extend it,
  never overwrite it.
- **Notebooks call `src/`**, not the reverse. A cell that reimplements model logic
  duplicates the code and drifts from it.
- **Clear outputs before committing**, or regenerate them in the same change. A stale
  stored output is a claim nobody can check.
- **Do not promote a notebook display to a finding.** Simulation output supports a
  software or model claim only; human and philosophical claims need separate evidence.
- Keep execution local and deterministic; set seeds explicitly and do not add network
  calls.
