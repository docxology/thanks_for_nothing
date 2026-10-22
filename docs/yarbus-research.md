# Yarbus source reconstruction and gaze extension dossier

Research date: 2026-10-15. The preserved Yarbus source reproduces the **before** bars of Figure 5 to their published one-decimal precision. Its **after** bars have no corresponding executable condition in the preserved notebook. A new learned intervention must therefore be reported as an extension. The notebook's embedded bar image disagrees with both its current code and the published before bars.

Integration status: version 0.5 implements selected proposals below through
[the gaze experiment contract](gaze-experiments.md): exact source-before replay,
two separate transfer bridges, active information gain, structural-access and
sampling controls, paired risk intervals and descriptive path metrics. The
proposal list remains a research record; neutral-only recall, full parameter
factorials, pixel inference, empirical gaze and persistent context learning are
future designs rather than implemented claims.

## Sources and identity

The primary paper is Elizabeth L. Fisher, Lars Sandved Smith and Jakob Hohwy, *Computational mechanisms of gratitude practice*, PsyArXiv v1, [DOI 10.31234/osf.io/xm25y_v1](https://doi.org/10.31234/osf.io/xm25y_v1). The local paper text and DOCX supply the inspected Methods, Results, Figure 5 and Code Availability. The OSF website/API did not load through the research browser during this investigation; local preserved metadata supplies the publication date, 2025-11-01, and is not a fresh verification of OSF status. Numerical conclusions below use the preserved source bytes directly.

| Source | SHA-256 | Inspected location |
| --- | --- | --- |
| [Original gratitude notebook](https://colab.research.google.com/drive/1OaYkfpko5RO1JIKgj-Ayb_tNfdTcmt0z) | `1b8a0400ba6c457d1da8ca28a369f60be2f367fb760a794c78ce7125a321ceb6` | 16 cells; scientific cells 1, 5, 8, 10, 12, 14 |
| [Original gaze notebook](https://colab.research.google.com/drive/1D6KJIQgzZhpKOaX4WKgjWl10xG_ZoMdO) | `ab9f36b515d1534d24b7e676841fa5cea7c264370f6ee566798c8b1b3de62510` | 3 cells; numerical class and comparison in cell 1 |
| [Paper text](../data/sources/source-paper.md) | Recorded in the research artifact manifest | Methods: Yarbus Task and Stages 1–4; Results: Figure 5; Code Availability |

Cell indices are zero-based. The paper's Code Availability points to [gratitude Colab](https://colab.research.google.com/drive/1OaYkfpko5RO1JIKgj-Ayb_tNfdTcmt0z) and [Yarbus Colab](https://colab.research.google.com/drive/1D6KJIQgzZhpKOaX4WKgjWl10xG_ZoMdO). These links identify provenance; no claim is made that the live notebooks still equal the preserved bytes.

## Figure 5: what is reproduced

The research script extracts `YarbusActiveInference` and `calculate_group_occupancy` from the admitted notebook, seeds the original NumPy RNG once with 42, and executes positive then negative agents in each of five pairs, with 1,000 states per agent. This preserves the random draw order in `run_comparison`; separately reseeding each agent would be a different experiment. Counts include the initial neutral state, index 10. Results are state occupancy percentages, not measured fixation durations.

| Condition | Positive states | Negative states | Neutral states | Status |
| --- | ---: | ---: | ---: | --- |
| Source positive profile | 82.14 | 10.98 | 6.88 | Executed; rounds to Figure 5 before agent 0.7: 82.1, 11.0, 6.9 |
| Source negative profile | 54.62 | 11.80 | 33.58 | Executed; rounds to Figure 5 before agent 0.3: 54.6, 11.8, 33.6 |
| Paper after agent 0.7 | 90.1 | 6.1 | 3.8 | Visually transcribed from DOCX Figure 5; not reproduced |
| Paper after agent 0.3 | 90.6 | 2.3 | 7.1 | Visually transcribed from DOCX Figure 5; not reproduced |

The embedded notebook bar image instead shows approximately 38.1/38.3/23.6 and 36.9/40.1/23.0. It is an unqualified stored output, not a reference oracle. The image was extracted without alteration and inspected. Figure 5 was extracted from `word/media/image5.png` of the preserved DOCX and inspected separately. The after values were not used to tune parameters.

## Executable source map and discrepancies

All gaze details in this section are directly inspectable in [Yarbus cell 1](https://colab.research.google.com/drive/1D6KJIQgzZhpKOaX4WKgjWl10xG_ZoMdO); paper comparisons refer to [Methods, Yarbus Task, and Figure 5](../data/sources/source-paper.md).

| Component | Exact implementation | Consequence |
| --- | --- | --- |
| State and outcome axes | 13 states: 0–4 positive, 5–9 negative, 10–12 neutral; observation rows positive, neutral, negative | Plot grouping uses a different ordering: positive, negative, neutral. State-count baseline is 5/13, 5/13, 3/13, not equal thirds. |
| Process `a1` | Deterministic 3×13 categorical map | This is not literally a square identity matrix, despite the paper's wording. |
| Model `A1` | Positive profile: positive columns `(0.7,0.2,0.1)`, others uniform; negative profile: negative columns `(0.1,0.2,0.7)`, others uniform | These are hand-set templates, not fitted agent-specific parameters or an explicit scalar precision transformation. |
| Observations | `infer_posterior_state` samples `A1[:, x1[t]]` | Declared process `a1` is unused in sampling. Independent 100-state probes found 46 and 66 observations incompatible with `a1`; the probe seed/state follows the captured script. |
| Preferences | `C = [2,0,-2]`, observation order positive/neutral/negative | Both profiles prefer positive outcomes. Profile names denote likelihood structure, not different preference vectors. |
| Policy score | `G[a] = -dot(A1[:,a],C) + 0.5*H(A1[:,a]) + Normal(0,0.1)` | Conditional sensory entropy is penalized. This term alone is not expected information gain about an uncertain hidden cause. |
| Policy sampling | `softmax(-1.5*G)` over 13 immediate destinations | The so-called temperature multiplies the score, so it acts as inverse temperature. No multi-step planning, movement cost, revisit memory or learned salience. |
| State dependence | `current_state` is assigned but unused; `G` ignores posterior and observation history | Changing state/posterior with RNG held fixed gives identical scores in a direct probe. The fixation policy is stationary apart from fresh noise. |
| Transition tensor | `B1[action,next,current]`; `B1[i,i,:]=1`; indexed as `B1[u,:,x1[t]]` | Internally correct deterministic destination control. A mistaken action-last audit would falsely flag this source. |
| Posterior | Bayesian update of `X1bar`; next prior is a known selected location | Posterior does not drive policy. Location uncertainty largely disappears after the initial action. |
| Learning and intervention | No update of `A1`, no gratitude import, no before/after loop | Direct probes confirm unchanged `A1`; the labels “Luckiness agent 0.7/0.3” do not bind to a luckiness parameter. |
| Final policy | Last column is zero because no next action is sampled | Exclude the terminal column when testing policy normalization. `Pibar` is allocated but never populated. |
| Occupancy | `calculate_group_occupancy` correctly pools equal-length runs | Its denominator assumes nonempty equal-length runs. An unused nested per-state helper overwrites counts across runs instead of accumulating. |
| Plot geometry | Hand-authored coordinates; first 20 states; cubic interpolation; zero jitter | Lines are illustrative interpolation, not recorded eye movements or saccade dynamics. Cubic curves can overshoot locations. |
| Plot RNG | Display helper resets global seed to 0 and still samples zero-scale jitter | Plotting changes global RNG state; comparison simulations occur before plotting in the original entrypoint. |

The two trajectory helpers repeat these coordinates:

```text
positive: (1,6), (2,6), (1,5), (2,5), (1.5,6)
negative: (5,1), (6,1), (5,2), (6,2), (5.5,1.5)
neutral:  (2,2), (1,3), (2,1.5)
```

The notebook contains no painting image loader, pixel coordinates, registration transform or region polygons. Figure 5 combines the painting with trajectories externally; its exact image and montage transformation cannot be recovered from the notebook. Gaze-region valence assignments are model assumptions, not measured affective ratings.

## Relation to the gratitude notebook

The following is source inspection, not a claim that the full gratitude notebook was rerun by this research task. Parent implementation owns full replication.

| Cells | Paper link | Source behavior and extension implication |
| --- | --- | --- |
| 1 | Stage 1 | 1,000 evenly spaced luckiness values; seven 12-step days; transition columns use luckiness. Likelihood weights accumulate `2*sum outer(observation,posterior)` without column normalization. Save occurs before daily learning, so day index 6 is the start of day seven. |
| 3, 9, 15 | Illustrative five-agent figures | Plot indices 0–4 while titles say 0.1/0.3/0.5/0.7/0.9; under the 1,000-agent grid those indices are near 0.1. Corrected plots must select by actual parameter value. |
| 5, 12 | Belief updating task | 70 trials with separately regenerated Python `random.uniform(0.2,0.7)` priors before/after; NumPy samples an optimism state from the learned posterior. Bind both RNGs and paired priors for a corrected causal comparison. |
| 8, 14 | Same-day assessment | Inspect explicitly generated shared observations rather than assuming identical transitions imply identical experiences. These are separate assessment cells. |
| 10 | Stage 3 | Uses fixed persistent transition columns `(0.7,0.3)` and `(0.3,0.7)`, rather than the original agent luckiness; observation process also changes to columns `(0.7,0.2,0.1)` and `(0.1,0.2,0.7)`. |
| 10 | Recall intervention | Selects the earliest three positive **or neutral** observations in temporal order and forces their posterior to `(1,0)`. This differs from the paper's three good observations and is not a finite precision update. Fewer than three eligible observations means fewer updates. |
| 10 | Post-recall learning | Accumulates unnormalized weights with learning rate 2, forgetting factor 1. `A1 = A_matrices[luck,6]` creates a NumPy view and in-place updates mutate baseline storage. Corrected branches need independent copies and explicit concentration-to-likelihood normalization. |

No source cell transfers the learned 3×2 gratitude parameters to the gaze notebook's 3×13 parameters. Any proposed map is a new, declared scientific assumption requiring its own control. The paper explicitly describes manipulating gaze likelihood precision, which supports a proof-of-concept interpretation; it does not provide the missing executable after condition.

## Primary scholarship checked

| Primary source and actual availability | Relevant bounded support |
| --- | --- |
| Alfred L. Yarbus (1967), “Eye Movements During Perception of Complex Objects,” *Eye Movements and Vision*, pp. 171–211, [DOI 10.1007/978-1-4899-5379-7_8](https://doi.org/10.1007/978-1-4899-5379-7_8). Publisher metadata/abstract inspected; full chapter subscription restricted. | This is the complex-scene chapter. The gratitude bibliography instead links the stationary-object chapter, pp. 103–127, DOI suffix `_4`. No claim of direct inspection of Yarbus's full experimental account. |
| Monica S. Castelhano, Michael L. Mack, John M. Henderson (2009), “Viewing task influences eye movement control during active scene perception,” *Journal of Vision* 9(3):6, 1–15, [DOI 10.1167/9.3.6](https://doi.org/10.1167/9.3.6). [University of Edinburgh publisher PDF](https://www.pure.ed.ac.uk/ws/portalfiles/portal/12627795/CASTELHANO_MS_Viewing_task_influences_eye_movement_control_during_active_scene_perception.pdf) downloaded and inspected. | Twenty participants, search versus memorization instructions. Task changed region selection and aggregate gaze measures; individual fixation durations and mean saccade amplitudes did not show the same task effects. Introduction identifies viewing-order confounding and sparse qualitative reporting in the classic demonstrations. Supports task manipulation and multiple gaze metrics, not gratitude efficacy. |
| M. Berk Mirza, Rick A. Adams, Karl Friston, Thomas Parr (2019), “Introducing a Bayesian model of selective attention based on active inference,” *Scientific Reports* 9:13915, [DOI 10.1038/s41598-019-50138-8](https://doi.org/10.1038/s41598-019-50138-8). Publisher full text inspected and captured. | Context-dependent sensory precision changes task-relevant information gathering. Expected epistemic value concerns posterior change about hidden causes, distinct from expected reward and parameter novelty. Data Availability identifies SPM `spm_MDP_VB_X.m`; that is an availability statement, not a reconstruction of its simulations here. |

## Artwork acquisition

An unedited original JPEG of Edvard Munch's *The Scream* (1893), accession NG.M.00939, was acquired from the [Wikimedia Commons file record](https://commons.wikimedia.org/wiki/File:Edvard_Munch_-_The_Scream_-_NG.M.00939_-_National_Museum_of_Art,_Architecture_and_Design.jpg). The [museum record](https://www.nasjonalmuseet.no/en/collection/object/NG.M.00939) identifies Nasjonalmuseet and photographer Børre Høstland. The Commons page marks the underlying artwork public domain and the digital reproduction CC BY 4.0. Preserve the reproduction attribution and [license link](https://creativecommons.org/licenses/by/4.0/) and identify overlays/resizing as changes.

Asset: `scream-original.jpg`, 6,703×8,322 pixels, 12,490,847 bytes. SHA-256: `a822bce9558bb02b36db10d4fa5e533c077feeb267798bce57c61fe3bc8d534d`. SHA-1 `3aa3e3658b8643fce5afb6c511ea5169a246b5e2` matches the Commons file checksum. The downloaded bytes were visually inspected; they are not a crop of Figure 5. A new background can use this asset with a declared coordinate registration, but is not the recovered authors' exact montage.

## Proposed extensions and discriminating controls

These are proposed experiments, not completed results or empirical claims. Bind all chosen tensors, transfer rules, scene layouts, seeds and treatment doses to GNN declarations.

1. **Learned gratitude-to-gaze transfer.** Run matched pre/post gratitude learning; transfer normalized learned outcome beliefs through an explicitly declared rule to scene inference. Hold scene, preferences and observation noise fixed. Use no-recall, random-recall, neutral-only recall and sham-transfer controls. Measure pre/post occupancy and held-out outcome log loss; increased positive occupancy alone cannot establish better calibration.
2. **Active visual inference.** Introduce uncertain scene features or context that observations actually resolve. Compute expected information gain by exact outcome enumeration and posterior KL, independently compare with entropy reduction, and separate it from preference value and movement cost. Test fully known scene (zero information gain), identical likelihood columns (zero information gain), and a diagnostic two-hypothesis scene (strictly positive information gain). Compare adaptive sampling with yoked/random trajectories at the same observation budget.
3. **Revisable structural priors.** Represent a fixed valence/region partition as one hypothesis and context-dependent alternatives as competing hypotheses. The inspected Realizing Emptiness declarations distinguish prior precision, metacognitive access and sector-label revisability; use these as separate intervention axes. Compare rigid, inspectable and revisable hypotheses under both stable and changed scenes. Score prequential log loss, posterior calibration and change adaptation. Lower certainty is not automatically a success: an accurate stable prior must remain useful.
4. **Practice controls.** Declare non-reification as the modeled capacity to revise a partition when evidence warrants it, distinct from positive-valence preference, uniform random gaze or flattening every belief. Include true stable structure, misleading observations, zero access, zero structural change, matched entropy and irrelevant label permutation. Report cost or deterioration where revision is unnecessary.
5. **Gaze metrics with independent meaning.** Report per-state and per-category occupancy, occupancy relative to available region counts, unique-region coverage, revisit rate, transition entropy, Euclidean step length under declared coordinates, and held-out scene prediction. Keep equal-duration occupancy distinct from dwell-time measures. Use unsmoothed points for metrics; interpolation is display-only. Separate transient first fixation from later sampling.
6. **Robustness and identifiability.** Factorially vary source precision, preference strength, observation noise, sensory availability, learning dose and movement cost. Paired seeds and held-out scenes estimate simulation variability. Swapping valence labels while holding geometry fixed, and swapping geometry while holding valence fixed, distinguish semantic from spatial effects. Check whether preference changes alone reproduce an occupancy effect before attributing it to learning or structural revision.

The relevant local Realizing Emptiness sources inspected are `src/modeling/specifications/practice_mapping.gnn.md`, `opacified.gnn.md`, `post_dual.gnn.md`, `separation_constrained.gnn.md` and `qrf_boundary.gnn.md` in its standalone checkout. These are design references; production must bind the imported dependency's pinned revision rather than silently consuming a different live checkout. All resulting experiments remain finite software models, without a gate for human gratitude, contemplative attainment, clinical outcomes, or neural mechanisms.

## Reproduction receipts

Receipt root: `/Volumes/GitVault/Local/evidence/thanks-for-nothing-gaze-20261015/research/`. `inspect_sources.py` is the exact executable research probe; `inspection.log`, `source-inventory.json` and `source-five-run-states.npz` record its full run. `paper-figure-5.png` and `yarbus-cell-1-output-1.png` retain the visual comparison. Primary web captures, original artwork and HTTP headers are retained alongside `artifact-manifest.json` with lengths and SHA-256 values. The repository's selected header copies omit response-cookie fields and normalize line endings; their manifest records both the release-copy and original-capture hashes. Original headers remain in external task evidence.

Invocation from the repository after binding the supplied external environment:

```bash
uv run --no-sync python "$RESEARCH_RECEIPTS/inspect_sources.py"
```

The recorded runtime has both `sys.prefix` and `sys.base_prefix` on GitVault. The complete environment binding and invocation are in `run-research.sh`; cache, temporary files and bytecode policy are explicit there.

| Acceptance scenario | Binary observable | Captured artifact |
| --- | --- | --- |
| Preserved notebook admission | Both SHA-256 assertions pass | `source-inventory.json` |
| Figure 5 before replication | Both percentage vectors round exactly to published before labels | `source-inventory.json`, `source-five-run-states.npz` |
| Nonvacuous comparison | Reversing category order fails equality to published vectors | `source-inventory.json` |
| Claimed deterministic process counterexample | At least one sampled observation has zero probability under `a1` for each profile | `source-inventory.json` |
| Learning/history inspection probe | `A1` unchanged and equal-RNG policy scores invariant to changed state/posterior | `source-inventory.json` |
| Artwork identity | JPEG size/shape verified, SHA-1 equals source record, SHA-256 captured | `artwork-provenance.json` |
| Primary source availability | Saved files nonempty; chapter access limitation retained | `artifact-manifest.json`, HTML/PDF receipts |

No after-reproduction pass is recorded. No proposed extension is marked implemented by this research dossier.
