# Original notebook reconstruction and bounded audit

The preserved notebooks are distinct source artifacts, not the paper itself and not
the corrected experiments. `data/sources/notebook_cell_manifest.json` records the
whole-file and per-cell SHA256 digests, executed definitions, and each adapted
integer literal. All cell indices below are zero-based. Stored notebook outputs
are not treated as execution evidence.

## Admission and execution

`run_source_reconstruction(seed=2025, agents=1000, days=7, steps=12)` admits
`gratitude_original.ipynb` only at SHA256
`1b8a0400ba6c457d1da8ca28a369f60be2f367fb760a794c78ce7125a321ceb6`.
It extracts cell 0's epsilon-softmax definition and runs cells 1, 5, 8, 10, 12,
and 14 in order. NumPy RandomState and Python Random instances isolate and seed
original sampling APIs. Installation, plotting, Colab exports and cached outputs
are excluded. This is a headless numerical reconstruction, not a complete Colab
session replay.

The adapter replaces every integer literal equal to 1000, 7, 12, 6, or 11 in
these six cells with agents, days, steps, days−1, or steps−1 respectively. Inspection
of every substitution in the manifest finds only array dimensions, loop limits,
and last-day/last-step indices. No matching literal is a learning rate, clamp
count or other mathematical parameter in this pinned source. This substitution
strategy is safe only with the digest restriction; it is not a generic notebook
parameterization mechanism. Default dimensions leave all literals unchanged.

`run_yarbus_reconstruction(seed=42, steps=100, agent_type="positive")` admits
`yarbus_original.ipynb` only at SHA256
`ab9f36b515d1534d24b7e676841fa5cea7c264370f6ee566798c8b1b3de62510`.
It extracts only the `YarbusActiveInference` class from cell 1, retains the source's
13 states and initial state 10, and isolates NumPy sampling. It does not execute
the comparison function, plot smoothing, installation, downloads or main block.
The source's positive/negative precision profiles are explicit fixed profiles;
this notebook does not import a learned likelihood from the first notebook.
That implementation fact does not contradict a paper explicitly manipulating
precision as an illustrative second task.

## First notebook: measured behavior and interpretation

- The 1000 agents occupy a deterministic evenly spaced luckiness grid from 0.1
  to 0.9. They are not 1000 independent replications at a single setting.
- Learned A entries are unnormalized counts subsequently used directly as
  likelihood weights. For a prior `[0.5, 0.5]`, equal-shaped columns with masses
  18 and 2 yield posterior well approximately 0.9000; normalizing those columns
  yields 0.5. This identifies sensitivity to accumulated column mass, rather
  than establishing that the model must use a different learning interpretation.
- Baseline snapshots in cell 1 are saved before daily learning. Cell 10 saves
  intervention snapshots after daily learning. At the original dimensions,
  baseline day-index 6 therefore contains six completed days of updates.
- `A1 = A_matrices[luck, 6]` is a NumPy view. Cell 10 mutates the saved baseline
  snapshot; the adapter retains copies before and after this mutation.
- Cell 10 hard-clamps the first three positive OR neutral observations' posterior
  to `[1, 0]` (or fewer if fewer are available). Tests check the actual selected
  observations and ensure other observations are not exactly clamped.
- Baseline and intervention use different observation and transition processes.
  A before/after change therefore does not isolate the clamp alone.
- A boundary posterior `[well=1, poor=0]` selects index 0 in the updating task,
  while comments label index 1 optimistic. This is a state-label inconsistency;
  the counterexample does not invalidate all possible readings of optimism.
- The before/after updating-task priors are independently redrawn, not paired.
- The plotting selection of the first five agents refers to luckiness near 0.1,
  not five evenly distributed settings. The final digitized bin excludes 0.9.
- Cell 8 resets T to 12 before cell 10. Correct numerical cell order completes;
  a claim that ordinary execution necessarily fails because T remains 1 is false.
- Epsilon softmax retains small nonzero mass at an otherwise impossible state.
  This is an explicit numerical convention, not empirical evidence.

## Yarbus notebook: actual axes and numerical controls

The tensor assignment `B1[i, i, :] = 1` is used as
`B1[action, next_state, current_state]`. Under this **action-first** convention,
every action sets the next state to its target independently of current state.
All 169 action/current-state combinations are tested. Their priors sum to one,
and the prior argmax agrees with the actual next state. Reading the third axis
as action would yield identity matrices, but that is not the source's indexing.
There is no demonstrated transition normalization or zero-prior defect.

Observations are sampled from `A1`, the agent likelihood, although the class also
declares a deterministic environmental matrix `a1`. At seed 42 over 100 steps,
33 observations have zero probability under that declared environmental matrix.
An independent first-draw oracle verifies the implemented A1 sampling. This
separates a concrete implementation/model distinction from a statistical claim.

The exact implemented policy score is
`G = -A1.T @ C + 0.5 * H + Normal(0, 0.1)`, with
`H = -sum(A1 * log(A1 + 1e-10), axis=0)`. An independent seeded numerical oracle
matches it exactly. H is conditional sensory entropy (an ambiguity cost); calling
this term information gain does not implement mutual information or posterior
entropy reduction. Policies use `softmax(-1.5 * G)`; the final policy column is
unused and stays zero because no action is taken after the final observation.

Static reading of excluded plotting code additionally finds a global seed reset
in `plot_yarbus_trajectory` and cubic interpolation of discrete target visits.
Those drawn curves are illustrative trajectories, not measured eye movements.
The used group-occupancy helper accumulates counts across equal-length runs;
the unused nested per-state helper overwrites counts across runs. These excluded
helpers are documented as static observations, not numerically validated defects
in the executed class or the displayed group occupancy.

## Reproduction evidence

The resumed execution evidence is in `.omo/evidence/source-reconstruction-resume/`:

| Scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Digest admission, malformed inputs, replay, changed seed, source counterexamples and mathematical nulls | `uv run --no-sync pytest tests/test_source_reconstruction.py --override-ini addopts='' --cov=thanks_for_nothing.source_reconstruction --cov-report=json:.omo/evidence/source-reconstruction-resume/coverage.json` | 30 tests pass; source reconstruction coverage 100% | `pytest-rerun.txt`, `coverage.json` |
| Combined bounded source audit | `build_source_audit(Path.cwd())` | Source digests admitted; controls finite; Yarbus transition control true and sampling mismatch positive | `audit.json` |
| Original 1000 × 7 × 12 numerical dimensions | `run_source_reconstruction(root=Path.cwd())` | All captured arrays finite; expected dimensions recorded | `full-source-run.json`, `full-source-run.npz` |
| External interpreter identity | `sys.prefix`, `sys.base_prefix` | Both resolved paths lie on GitVault | `runtime.json` |

These scenarios establish bounded source behavior and reproducibility. They do
not validate human gratitude outcomes, clinical benefit, eye-tracking behavior,
or philosophical equivalence. They do not assert that every source distinction
is a bug or that the paper is invalid. The recovered files, preprint and journal
versions must retain separate provenance in scholarship records.

Source lookup supports installed wheels: without an explicit root it first uses
`thanks_for_nothing/resources/sources`, then the editable checkout's source data.
The wheel build bundles these immutable source datasets with their licensing and
provenance notices. An explicit root always selects that root's `data/sources`;
missing files raise `SourceInputError` and never silently fall back. Installed-wheel
qualification is performed separately by the coordinating worker. Two additional
checks cover default lookup and a real empty explicit root, bringing the targeted
suite to 32 tests (`pytest-complete.txt`).

The initial strict-check failures remain preserved in `ruff-initial.txt` and
`typing.txt`; later cleanup resolves source namespace typing through frozen
Pydantic notebook, snapshot, prior and array models, and uses typed ndarray
slices and reductions at scalar boundaries. `typing-clean.txt` records zero
errors under the strict project configuration. `pytest-clean.txt` records
32 passing tests and 100% reconstruction coverage. `strict-cleanup-replay.json`
confirms all full-size source arrays and the combined audit exactly match the
pre-cleanup receipts. Source-model mathematics and the digest contract are
unchanged. The coordinating worker supplied the test package marker; Ruff now
passes for both owned Python files. The final combined command receipt is
`strict-final-pass.txt` in this evidence directory.
## New executable companions in version 0.5

The unchanged source notebooks remain reconstruction inputs. Three separately
authored companions execute package producers: `gratitude_absence.ipynb` is a
small introduction; `belief_updating.ipynb` replays the original 1,000-agent
numerical scope and the corrected canonical learning study; `gaze_emptiness.ipynb`
reproduces source-before occupancy and runs learned transfer and active inquiry.
The latter two expose editable code, checks, figures and every exploratory gaze
interval. They do not claim complete replay of the original Colab interfaces or
recovery of missing source-after code. See [the gaze contract](gaze-experiments.md).
