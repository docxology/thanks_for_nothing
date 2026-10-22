# Reading the manuscript and its evidence

Start with the [rendered manuscript](../output/manuscript.html) or
[printable version](../output/manuscript.pdf). Both contain the main argument,
technical supplement and references. The main text explains the question,
comparison, finding and interpretation; the supplement makes those explanations
auditable through equations, complete results, controls and prospective study
designs. Figure and equation numbers are generated, so use named links rather
than copying an ordinal into notes.

After the cover, the conceptual graphical abstract distinguishes evidence,
missingness, counterfactual value and revisability. The experimental graphical
abstract follows the controlled comparisons and limits of each claim. The
GNN model card occupies physical page four, followed by the contents on page five.
Its time-unrolled Bayesian diagram defines tensor semantics, while the parsed
dependency graph and inventory identify actual execution roles. The complete
card companion exposes each exact declaration and numerical consumer record.
Methods separates paired recall
and absence, enacted inquiry, learned scene transfer, and joint scene/encoding
inquiry into distinct sections. Existing section identifiers remain stable for
review comments and supplemental links.

## Follow a research question

| Question | Main argument | Inspect the supporting detail |
| --- | --- | --- |
| What changes when a recorded absence, an unavailable record and a counterfactual value are distinguished? | [Operational meanings](manuscript/manuscript.md#operational-meanings-of-nothing) and [recall results](manuscript/manuscript.md#sec-main-recall) | [Observation/value model](manuscript/supplement.md#sec-absence-model), [absence information](manuscript/supplement.md#fig-absence-information) and [valuation-only null](manuscript/supplement.md#fig-appreciation) |
| Does selected rehearsal improve independent prediction? | [Paired design](manuscript/manuscript.md#sec-main-pairing) and [recall interpretation](manuscript/manuscript.md#sec-main-recall) | [Scoring definitions](manuscript/supplement.md#sec-scores), [world-specific results](manuscript/supplement.md#fig-calibration), [mixture sensitivity](manuscript/supplement.md#fig-weighting) and [all primary intervals](manuscript/supplement.md#supp-primary-intervals) |
| When does costly inquiry permit useful revision or retention? | [Practice results](manuscript/manuscript.md#sec-main-practice) and [central proposal](manuscript/manuscript.md#gratitude-for-the-practice-of-realizing-emptiness) | [Policy mechanism](manuscript/supplement.md#fig-practice-mechanism), [activity versus access](manuscript/supplement.md#fig-practice-policies), [exact decisions](manuscript/supplement.md#sec-exact-results) and [practice intervals](manuscript/supplement.md#supp-practice-intervals) |
| Does a changed scanpath identify better prediction or an inquiry-specific advantage? | [Gaze methods](manuscript/manuscript.md#sec-main-gaze-method), [gaze results](manuscript/manuscript.md#sec-main-gaze) and [measurement implications](manuscript/manuscript.md#sec-main-gaze-discussion) | [Source reconstruction](manuscript/supplement.md#fig-yarbus-reconstruction), [learned transfer](manuscript/supplement.md#fig-gaze-transfer-summary), [scene risk and cost](manuscript/supplement.md#fig-gaze-inquiry-summary) and [joint bounds](manuscript/supplement.md#supp-gaze-joint) |
| What distinguishes learning an encoding from using it for reference prediction? | [Scene/encoding results](manuscript/manuscript.md#sec-main-boundary) | [Conditional channels](manuscript/supplement.md#fig-boundary-information), [reference target](manuscript/supplement.md#sec-boundary-target), [outcome panels](manuscript/supplement.md#fig-boundary-outcomes) and [complete intersection bounds](manuscript/supplement.md#supp-boundary-joint) |
| What evidence would justify a human interpretation? | [Identification and empirical program](manuscript/manuscript.md#sec-main-identification) | [Comparator scholarship](manuscript/supplement.md#sec-comparators), [policy confounding](manuscript/supplement.md#eq:policy-identification), [inquiry study](manuscript/supplement.md#sec-empirical-inquiry) and [human gaze task](manuscript/supplement.md#sec-empirical-boundary) |

These source-file links identify the authoring passages. A raw Markdown viewer
may not follow a fragment that belongs to the other authoring component. The
composed HTML and PDF resolve main-text links to supplement sections, figures
and equations within the same document.

## Read the statistical displays

Read the outcome and comparison before its direction. An optimism readout,
predictive loss, positive-location occupancy, encoding score and activity cost
answer different questions. A favorable change in one does not establish a
benefit in another. [Statistics](statistics.md) defines the independent units
and estimands; [visualizations](visualizations.md) explains keys and units.

Pointwise confidence intervals, joint bounds, between-unit spreads and world
weighting ranges have different meanings. A weighting scenario changes the
target without adding observations. A proved null can be exact, while an
accidentally constant sample can leave an interval unavailable. Consult the
[uncertainty methods](manuscript/manuscript.md#sec-main-statistics),
[known-answer coverage](manuscript/supplement.md#fig-joint-coverage) and
[operating checks](manuscript/supplement.md#supp-diagnostics) before treating a
nominal confidence level as measured performance.

For the expanded simulations, follow the
[precision and design scope](manuscript/supplement.md#sec-simulation-precision)
to the [sample-size diagnostic](manuscript/supplement.md#fig-sampling-precision).
It reports the actual independent-unit ladder, signed effects and estimated
Monte Carlo error. The [design readings](simulation-design-research.md) explain
why larger cohorts, additional assessment outcomes, more resampling draws and
a broader crossed grid address different limitations.

## Trace a claim or prepare review notes

Use [generated facts](../output/reports/research_summary.md) for current run
quantities, the [variable ledger](../output/reports/manuscript_variables.json)
for numerical producers, and the
[figure source map](../output/reports/figure_source_map.json) for figure inputs.
The [scholarship guide](scholarship.md) distinguishes primary-text reading,
abstract access and metadata-only context. The
[main-text reading dossier](maintext-scholarship-research.md) records the
targeted sources checked for the expanded explanations.

A useful review comment names the section or figure, states the claim being
tested, and identifies the relevant alternative explanation or missing evidence.
Distinguish a source-reconstruction objection, a computational error, an
estimator limitation and a disagreement with the conceptual proposal. Those
can require different corrections even when they occur in the same paragraph.

For execution and delivery, use [reproducibility](reproducibility.md) and
[manuscript production](manuscript-production.md). A past approval belongs to
its recorded source and artifact hashes; it does not transfer automatically
to revised prose or rebuilt products. [Evidence ceilings](evidence-ceilings.md)
state what the simulation cannot establish about people or philosophical claims.
