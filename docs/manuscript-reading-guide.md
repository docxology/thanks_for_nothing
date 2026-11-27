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
| What changes when a recorded absence, an unavailable record and a counterfactual value are distinguished? | [Operational meanings](manuscript/manuscript.md#nothing-as-evidence-missingness-value-and-revisability-operational-meanings-of-nothing) and [recall results](manuscript/manuscript.md#positive-recall-changes-optimism-without-a-general-predictive-benefit-sec-main-recall) | [Observation/value model](manuscript/supplement.md#absence-observations-and-counterfactual-valuation-sec-absence-model-unnumbered), [absence information](manuscript/supplement.md#observed-absence-and-the-valuation-only-null-sec-absence-results-unnumbered) and [valuation-only null](manuscript/supplement.md#observed-absence-and-the-valuation-only-null-sec-absence-results-unnumbered) |
| Does selected rehearsal improve independent prediction? | [Paired design](manuscript/manuscript.md#separating-recall-recorded-absence-and-counterfactual-value-sec-main-pairing) and [recall interpretation](manuscript/manuscript.md#positive-recall-changes-optimism-without-a-general-predictive-benefit-sec-main-recall) | [Scoring definitions](manuscript/supplement.md#independent-predictive-evaluation-and-the-optimism-readout-sec-scores-unnumbered), [world-specific results](manuscript/supplement.md#paired-recall-optimism-and-predictive-loss-sec-recall-results-unnumbered), [mixture sensitivity](manuscript/supplement.md#world-heterogeneity-and-mixture-sensitivity-sec-mixture-results-unnumbered) and [all primary intervals](manuscript/supplement.md#complete-primary-interval-comparisons-supp-primary-intervals-unnumbered) |
| When does costly inquiry permit useful revision or retention? | [Practice results](manuscript/manuscript.md#effective-access-permits-revision-and-appropriate-retention-sec-main-practice) and [central proposal](manuscript/manuscript.md#gratitude-for-the-possibility-of-examining-ones-own-constructions-gratitude-for-the-practice-of-realizing-emptiness) | [Policy mechanism](manuscript/supplement.md#an-enacted-policy-for-examinable-representations-sec-practice-model-unnumbered), [activity versus access](manuscript/supplement.md#valuing-choosing-and-enacting-inquiry-sec-practice-results-unnumbered), [exact decisions](manuscript/supplement.md#exact-conditional-decisions-and-rare-selections-sec-exact-results-unnumbered) and [practice intervals](manuscript/supplement.md#complete-practice-interval-comparisons-supp-practice-intervals-unnumbered) |
| Does a changed scanpath identify better prediction or an inquiry-specific advantage? | [Gaze methods](manuscript/manuscript.md#transferring-learned-channels-to-active-scene-sampling-sec-main-gaze-method), [gaze results](manuscript/manuscript.md#access-advantages-do-not-establish-an-inquiry-specific-gaze-benefit-sec-main-gaze) and [measurement implications](manuscript/manuscript.md#what-gaze-confidence-and-first-person-reports-can-establish-sec-main-gaze-discussion) | [Source reconstruction](manuscript/supplement.md#reconstructing-and-extending-the-gaze-experiment-sec-gaze-results-unnumbered), [learned transfer](manuscript/supplement.md#reconstructing-and-extending-the-gaze-experiment-sec-gaze-results-unnumbered), [scene risk and cost](manuscript/supplement.md#reconstructing-and-extending-the-gaze-experiment-sec-gaze-results-unnumbered) and [joint bounds](manuscript/supplement.md#complete-joint-gaze-bounds-supp-gaze-joint-unnumbered) |
| What distinguishes learning an encoding from using it for reference prediction? | [Scene/encoding results](manuscript/manuscript.md#learning-an-encoding-differs-from-using-it-for-prediction-sec-main-boundary) | [Conditional channels](manuscript/supplement.md#gaze-on-a-scene-and-inquiry-into-its-encoding-sec-boundary-results-unnumbered), [reference target](manuscript/supplement.md#reference-frame-transfer-and-proper-boundary-scores-sec-boundary-target-unnumbered), [outcome panels](manuscript/supplement.md#gaze-on-a-scene-and-inquiry-into-its-encoding-sec-boundary-results-unnumbered) and [complete intersection bounds](manuscript/supplement.md#complete-sceneboundary-intersection-bounds-supp-boundary-joint-unnumbered) |
| What evidence would justify a human interpretation? | [Identification and empirical program](manuscript/manuscript.md#from-finite-mechanisms-to-an-identifiable-human-research-program-sec-main-identification) | [Comparator scholarship](manuscript/supplement.md#what-intervention-comparisons-identify-sec-comparators-unnumbered), [policy confounding](manuscript/supplement.md#an-enacted-policy-for-examinable-representations-sec-practice-model-unnumbered), [inquiry study](manuscript/supplement.md#testing-appreciation-access-and-appropriate-revision-sec-empirical-inquiry-unnumbered) and [human gaze task](manuscript/supplement.md#coupled-gaze-and-boundary-inquiry-in-a-human-study-sec-empirical-boundary-unnumbered) |

The source links open the relevant headings on GitHub. Figure links in this
guide open the section containing the figure. The composed HTML and PDF resolve
main-text links to supplement sections, figures and equations within the same
document.

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
[uncertainty methods](manuscript/manuscript.md#defining-estimands-and-testing-uncertainty-procedures-sec-main-statistics),
[known-answer coverage](manuscript/supplement.md#joint-gaze-uncertainty-and-the-cost-of-nominal-confidence-sec-joint-results-unnumbered) and
[operating checks](manuscript/supplement.md#statistical-operating-checks-and-model-sensitivity-supp-diagnostics-unnumbered) before treating a
nominal confidence level as measured performance.

For the expanded simulations, follow the
[precision and design scope](manuscript/supplement.md#simulation-precision-and-crossed-design-scope-sec-simulation-precision-unnumbered)
to the [sample-size diagnostic](manuscript/supplement.md#precision-across-independent-sample-sizes-sec-sampling-results-unnumbered).
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
