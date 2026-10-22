# Visualizations and captions

The opening graphical abstracts are a separate reading layer. The conceptual
page reuses the manuscript's symbolic operations for recorded absence,
missingness, counterfactual value and revisability. Symbols express definitions,
not new observations. The experimental page separates matched comparisons,
findings and limitations. Both resolve scientific quantities from the composed
manuscript ledger and export PNG, SVG and vector PDF. Their evidence links lead
to stable manuscript targets; they do not consume scientific figure numbers.
The [production guide](manuscript-production.md) describes their configuration
and source bindings.

The experimental abstract separates six controlled questions, with compact
conditional-model views and source-derived dimensions. Complete standalone GNN
instances include every query channel and both observation regimes. Native graphs
and the complete cards expose full instances as well as authoring inputs. The
tensor figure focuses on runtime families; the opening card lists authoring inputs.
The expanded cards are collapsible in HTML and preserve all values in linked JSON.

Physical page four adds the GNN Bayesian model card. Its temporal graph defines
the categorical POMDP factorization conditional on actions; outcome preferences
guide native action selection outside that conditional graph. The separate
declaration graph is parsed from GNN rather than treated as a causal DAG. The
inventory displays all admitted dimensions, consumers and source-digest prefixes.
Complete model cards preserve full digests, arrays, settings, raw declarations,
native graphs and dependency provenance in accessible HTML and typed JSON.

The main-text `world_traditions` atlas is a qualitative exception to the numerical
figures: aligned questions compare selected named witnesses without a score,
heatmap, geography or inferred lineage. The [atlas guide](wisdom-traditions.md)
explains its declarative content and source-linked expandable companion. Each
row retains its own object of relinquishment and response; a missing gratitude
instruction is stated rather than filled with an invented equivalence.

The main paper explains the cognitive setting before interpreting a number.
The experiment overview asks, for each task: what changes, what is held fixed,
what is assessed independently, and which control limits the proposed reading.
The same [task registry](../src/thanks_for_nothing/experiment_overview.py) generates
the overview and the technical crosswalk.

## Main argument and complete evidence

The supplemental GNN views are generated from the real parsed declarations.
`gnn_model_graph` groups only identical node/edge lists; `gnn_model_tensors`
reads admitted runtime-family dimensions and instance counts. The opening card
distinguishes native, local and protocol roles. GNN's own
per-model network PNGs and statistics are retained under `output/gnn/`.
The [model contract](model-contract.md#admission-before-computation)
describes the source and execution bindings. These are dependency graphs, not
estimated causal networks; shared topology supplies no doctrinal or psychological
equivalence.

Main Results pair the recall, enacted-practice, gaze and scene/encoding situations
with selected readouts. The detailed task settings, complete comparison charts,
bar plots, scanpaths, exact decisions, parameter sensitivity and operating checks
remain in the technical supplement. Existing stable anchors remain available.

[Figure placement](../src/thanks_for_nothing/figure_placement.py) checks that the
required result situations appear in Results and that detailed comparisons remain
supplementary. The executable inventory in
[visual tokens](../src/thanks_for_nothing/visual_tokens.py) is authoritative;
current figure and equation counts are [generated](../output/reports/research_summary.md).

## Shared meanings and visible keys

The [activity/access figure](manuscript/supplement.md#fig-practice-policies)
pairs a solid gray activity bar with a hatched teal access bar, preserving the
distinction in grayscale. Numeric labels expose exact zeros that otherwise have
no visible bar. Labels round finite means to two significant digits; small
positive rates retain significant digits instead of being printed as zero.
These are descriptive rates over repeated windows, not independent-window
confidence estimates or measures of human intervention delivery.

The [exact-decision figure](manuscript/supplement.md#fig-exact-decision) repeats
the same finite count masses on linear and logarithmic axes. The linear view
preserves the relative mass around each process mode; the log view makes rare
selection tails visible without replacing a nonzero probability with zero.
Dotted boundaries are derived from adjacent counts with different decisions.
They are selection boundaries, not significance thresholds. Read the conditional
selection probability by summing masses over the open-family counts, rather
than treating a plotted count mass as the probability of selecting that family.
The [exact-decision guide](exact-decisions.md) gives the corresponding estimands.

[DESIGN.md](../DESIGN.md) and the shared style/tokens define colors, type, physical
placement and export. Every scientific figure has an explicit key. Reuse labels,
markers and line styles so color is not the only distinguishing channel.
Palette-role aliases are scoped to the named experiment; a shared color does not
make different interventions scientifically identical.

Keep state probabilities, policy masses, losses, costs and information in their
own units. Use labeled sequential scales for probability matrices and signed
scales centered at zero for contrasts. A path connects sampled model sites;
nonspatial encoding questions are displayed on a decision timeline.

## Captions are an interface

Learning trajectories now retain all independent agents. Mean curves and
between-agent interquartile bands accompany paired changes from each agent's
own no-recall trajectory. The bands describe unit spread, not confidence for
the mean. Encoding-allocation segments similarly show pooled whole-unit
interquartile ranges across the fixed cells, including between-cell variation.
The statistical coverage plot uses an explicitly labeled detail axis so small
coverage departures remain legible; the joint rare-event control keeps its
full probability scale.

Each record in [captions.yaml](manuscript/captions.yaml) supplies:

- A short title identifying the question.
- The task or comparison, including what the agent sees or can change.
- Instructions for reading panels, symbols and units.
- The independent unit, interval procedure and nominal level, or an explicit
  statement that the display is deterministic, descriptive or illustrative.
- An interpretation limit that prevents a model result from becoming a human claim.

Caption variables use the same numerical injection as the body. Native figure
labels derive quantities from the records; shared display scaling has one
authority. Figure numbers and cross-references are automatic.

Loss contrasts state positive recall minus its named comparator and identify
the favorable direction. Diagnostic world plots use the admitted world range
with clearance for offset markers; zero-reference lines span the panel. Keep
headroom for the data and intervals, since keys occupy a separate footer.

## Integrity and actual inspection

The [source map](../output/reports/figure_source_map.json) records producer and
image digests, dimensions, keys, colors and font measurements. Vector admission
checks actual key labels and palette values. Export rejects text crossing its
physical canvas; it does not prove that every pair of internal labels is separate.

Inspect the PNGs at publication size, every final PDF page, notebook image output
and both normal and narrow HTML. Keep interval methods separate from unit spread
and fixed-grid sensitivity. Reject missing keys, repaired-hash tampering and
unreadable annotations rather than accepting a checksum or a screenshot alone.
The [reproducibility guide](reproducibility.md) describes the final evidence boundary.

## Figure-by-figure interpretation checks

This register records the initial manual review and the interpretation retained
for regeneration. Final capture hashes and acceptance judgments belong to the
dated output review, after all figures and the full manuscript have been rendered.

| Figure | Pattern to inspect and retained interpretation |
| --- | --- |
| gnn_model_graph | Nodes and arrows must match parsed GNN declarations; preserve cycles without a causal-DAG claim. |
| gnn_model_tensors | Dimensions must follow admitted arrays; native, finite and protocol roles stay distinct. |
| concept_map | A definition diagram; arrows are declared relations, not measured causal effects. |
| concept_operations | Finite operations and conceptual analogies remain separate from attainment. |
| experiment_overview | Task and control crosswalk; all numerical settings must come from records. |
| task_settings | Authored categorical scene channels; painting pixels are not model inputs. |
| boundary_task | Explicit spatial/structural routes and shared budget; no empirical neural pathway claim. |
| recall_situation | Readout and predictive loss need separate directions and paired assessment. |
| learning_trajectories | Replace a single-agent illustration with ensemble means, IQRs and paired daily changes. |
| calibration_by_world | Inspect cancellation and narrow intervals; retain whole-agent spread and all worlds. |
| paired_contrasts | Exact valuation zeros require the intervention identity, not finite-sample constancy. |
| paired_spread | Segments are within-world unit quartiles; they are not confidence bounds. |
| weighting_sensitivity | Straight ranges follow a convex mixture identity; they do not add observations. |
| appreciation_null | Nonzero valuation can coexist with exact zero change in inference; no invented variance. |
| absence_information | A small deterministic worked comparison is appropriate; its null is a missingness convention. |
| attention_policies | Descriptive policy mass is not measured gaze; preserve small nonzero probabilities. |
| sensitivity | Expand the crossed grid; inspect both sign and magnitude without claiming global robustness. |
| statistical_calibration | A labeled detail scale exposes coverage departures; preserve failed or unavailable methods. |
| practice_situation | Enacted steps and held-out assessment remain distinct from aspirational value. |
| practice_mechanism | Implemented and proposed links need visibly different line meanings. |
| practice_policies | Zero access/activity bars remain labeled; activity and access use distinct fills. |
| practice_revision | A zero event count is not impossibility; windows do not enlarge the independent cohort. |
| exact_decision | Linear/log views retain rare positive mass and conditional decision scope. |
| yarbus_reconstruction | Pinned before-only source behavior; unavailable after learning must stay unavailable. |
| gaze_situation | Transfer and active sampling use different mechanisms and assessment targets. |
| gaze_transfer_paths | Selected paths illustrate individual runs; no population inference from path shape. |
| gaze_transfer_summary | Shared valuation outcomes are exact; stratum means and paired intervals have different roles. |
| gaze_inquiry_paths | Individual illustrative trajectories; low movement does not prove useful information. |
| gaze_inquiry_summary | Open-policy comparators test incremental inquiry; cost is separate from prediction. |
| gaze_joint_uncertainty | Distinguish proved zeros, estimated bounds and unavailable constants. |
| joint_coverage | Keep the full probability scale so rare-event coverage failures remain visible. |
| boundary_situation | Anchored prediction depends on the stipulated reference intervention. |
| boundary_information | Uniform marginals can coexist with informative action-response pairs; check the joint law. |
| boundary_gaze_outcomes | Label-only/sham identities can produce exact overlap; keep restricted-support offsets. |
| boundary_gaze_allocation | Add pooled whole-unit IQRs so means do not hide cell and replicate variation. |
| boundary_gaze_convergence | Nested prefixes share units; stability alone does not establish precision or validity. |
| boundary_structure | Native mathematical comparators remain independent of mutable task parameters. |
| boundary_gaze_paths | Separate site paths from nonspatial query timelines; selected examples are illustrative. |
| sampling_precision | New display: signed means, one-MCSE whiskers and a conditional inverse-square-root guide. |
