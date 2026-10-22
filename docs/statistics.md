# Statistical contract

The target, independent unit, repeated measurements and uncertainty procedure
must be stated separately. [Generated current facts](../output/reports/research_summary.md)
supply actual cohort, contrast and draw counts; the admitted GNN declarations own
budgets. The manuscript retains complete numerical results and interval tables.

## Primary recall and exploratory extensions

The primary recall target is the equally weighted mean of paired pre/post changes
over fixed world strata. Each independently seeded agent-world unit contains all
paired conditions and its full trajectory. Days, replayed events and time steps
are not independent subjects. The target is conditional on the fixed grid,
not an estimated human population.

The primary family compares positive/no recall, random/no recall, absence-value/no
recall and positive/random recall on the optimism readout and binary Brier change.
World-specific diagnostics, observation log loss, weighting sensitivity and later
practice/gaze/intersection families remain exploratory. They do not silently
expand or replace the primary Holm family.

[Input admission](../src/thanks_for_nothing/statistics.py) rejects missing/duplicate
conditions, unmatched exposures/identities and unbalanced replicate sets.
[Outcomes](../src/thanks_for_nothing/outcomes.py) define each post-minus-pre target.

## Interval procedures and unavailable estimates

The packaged [analysis declaration](../src/thanks_for_nothing/models/analysis.gnn.md)
owns the pointwise error level, statistical stream offsets, nested diagnostic
budgets and companion-notebook budgets. Its admitted values are preserved in
`output/data/analysis_protocol.json`. Joint-region coverage and quantile-bracket
levels remain separately declared in the gaze model. Every returned interval
records its actual confidence level. Fields containing `ci95` retain their
historical serialization names; their level is the recorded `confidence`, rather
than a second fixed parameter hidden in Python.

Percentile intervals resample whole paired units within each fixed stratum and
use the declared linear quantiles of mean replicates. Independent tests check
interpolation against NumPy.

Studentized bootstrap intervals recompute each resample's within-stratum variance.
The observed standard error is not reused as the resample denominator.
Variance calculations first subtract each stratum's first observation, and each
bootstrap resample subtracts its own first observation. These exact translations
prevent constant decimal-valued samples from acquiring a spurious positive
variance through floating-point mean rounding. Bootstrap roots use the centered
means, retaining translation stability without a tolerance, jitter or discarded draws.
Zero observed variance or any zero resample variance makes that studentized
interval unavailable. The reason and draw count remain visible; failed draws
are not discarded and another method is not substituted.

For the centered Bernoulli control, `bootstrap_availability` integrates over the
original binomial count and computes the exact probability that every resample
has positive variance. The [derivation](manuscript/supplement.md#sec-bootstrap-availability)
states the strict policy and its decreasing availability as the draw budget grows.
The saved calibration record retains the complete count-wise decomposition;
the figure and results text derive their annotations from that record.
Availability, unconditional coverage and coverage conditional on availability
use different denominators. Only the first has this exact benchmark. The
[primary-source dossier](bootstrap-availability-research.md) separates the empirical
bootstrap lineage, failure-reporting guidance and the new finite calculation.

The analytic interval uses the same stratified variance with Welch-Satterthwaite
degrees of freedom. It is exact for a single Gaussian stratum and generally
approximate for finite-model contrasts. A constant sample yields a degenerate
analytic interval with undefined degrees of freedom. A mechanism-exact null
has its separate computational justification.

All procedures remain on the same samples. Nominal confidence states a target,
not a universal finite-sample coverage guarantee. The mathematical derivations
and complete interval records are preserved in
[the supplement](manuscript/supplement.md#sec-experiments).

## Tests and numerical tail precision

A sign-flip test requires symmetric or appropriately exchangeable paired
differences under its null; pairing or a zero mean is insufficient. Monte Carlo
p-values retain the exceedance-plus-one correction.

Pinned Realizing Emptiness supplies exact binomial tail bounds. Simultaneous
allocation qualifies the finite Monte Carlo tail approximations, and Holm
adjustment applies to p-values and bounds. Decisions use the admitted nominal
level: an adjusted upper bound below it rejects, a lower bound above it retains,
and overlap remains unresolved. Retention is not equivalence.

[Exhaustive sign enumeration](../src/thanks_for_nothing/estimation.py) is an
independent small-sample mathematical oracle, not a replacement for the canonical
Monte Carlo experiment. Hand-counted tails and exact ties challenge it.

## Heterogeneity, weighting and endpoints

World-specific paired means retain every interval method. Medians, quartiles and
positive-difference fractions describe independent-unit distributions; quartiles
are not confidence intervals.

For nonnegative weights summing to one, the convex envelope of fixed estimated
world means runs from their minimum to maximum. Leave-one-world-out estimates
equally weight the remaining worlds; that operation is undefined for a single
world. These are sensitivity scenarios conditional on estimated means, not
confidence bounds or new data.

Binary Brier and predictive observation NLL are losses: lower is better.
Brier alone does not isolate calibration from discrimination or resolution.
Optimism is a stipulated model readout. Counterfactual valuation leaves paired
belief, Brier and NLL inference unchanged by construction; a value can be nonzero
without new evidence. Entropy is neither correctness nor gratitude.

## Practice, gaze and intersection units

Practice averages each replicate's policy-minus-rigid held-out loss across
repeated windows before estimating a context-specific contrast. Calibration
selects the model; fresh assessment does not. Activity cost is separate from
predictive loss. [Exact count decisions](exact-decisions.md) have a conditional
finite target and do not receive a Monte Carlo effect interval.

Gaze transfer resamples complete paired agents within fixed worlds, preserving
both bridges and every endpoint. Active gaze first averages windows within a
replicate; different contexts use independent streams. Direct inquiry comparisons
against already-open utility and uniform sampling are necessary for an incremental
inquiry claim.

The scene/encoding study resamples paired replicates within fixed cells and keeps
the reference intervention explicit. Its separate family includes all declared
endpoints/comparisons. Proved constants require mechanism and record checks;
sample constants alone remain unavailable. [The joint guide](joint-uncertainty.md)
defines shared maxima, exact statuses, quantile brackets and translation controls.

## Known-answer statistical calibration

The [sampling diagnostic](manuscript/supplement.md#fig-sampling-precision) shows
signed whole-unit contrasts and estimated Monte Carlo standard errors across
declared nested prefixes. Repeated windows are averaged within a replicate;
fixed strata retain equal weights. Prefixes share earlier units and do not
provide independent confirmations. The inverse-square-root line is anchored to
the full-budget MCSE and is a reference guide, not a fitted result. See the
[primary-source design dossier](simulation-design-research.md) for the distinction
between simulation precision, resampling precision, sensitivity and model validity.

Independent fixtures span symmetric Gaussian null/shift, heavy tails, skew,
heterogeneous variance and discrete rare events. Their mathematical distribution
constants are independent controls; model experiment budgets come from GNN.
Methods share samples.

Coverage counts all independent experiments, including unavailable intervals as
noncoverage, while reporting availability separately. Exact binomial intervals
and Monte Carlo standard errors qualify rates. Skewed mean-zero differences can
violate sign symmetry. Undercoverage and unavailable rare-event regions remain
findings; neither seeds nor thresholds are retuned to make a method pass.

These checks qualify finite statistical procedures under stated conditions.
They are not human treatment power, gratitude efficacy or a realization measure.
