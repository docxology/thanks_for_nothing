# Exact evidence decisions and their limits

The [practice model](emptiness-practice.md) compares restricted and open priors
on the same calibration evidence. [The exhaustive oracle](../src/thanks_for_nothing/practice_exact.py)
enumerates every binary count under the existing admitted GNN declaration.
It introduces no parallel model default or Monte Carlo seed.

## Why adding an alternative need not help

Let the restricted prior be the open prior conditioned on a proper subset with
retained mass w. Open evidence is w times restricted evidence plus (1-w) times
the evidence of the complementary conditional prior. The open family wins
exactly when that complement has greater evidence.

The actual priors, retained mass and rational likelihood-selection inequality
are injected in [the technical derivation](manuscript/supplement.md#sec-exact-method).
They must follow the admitted support rather than a copied numerical inequality.
Both posteriors are fitted separately. `BMRComparison` supplies component algebra,
not a posterior-reuse shortcut across zero support.

Stable scalar log evidence decides the family. Independently computed native
KL-minus-accuracy free energies remain checked, but rounded subtraction does
not decide an exact tie. The equal-channel negative/retention control reproduces
the former floating-point tie defect.

## Exact quantities and numerical evaluations

Decimal strings from admitted tensors define rational coefficients. Fraction
products and sums give evidence ratios, posterior forecasts and count decisions.
Rational normalization derives both priors from the actual upstream-admitted
support. Reported logarithms and predictive losses are numerical evaluations.

The binomial coefficient cancels from an evidence ratio but remains necessary
when weighting count outcomes. Enumerating every count gives rational selection
probabilities for the process probabilities present in the GNN schedules.
The audit retains integer numerators/denominators, displays, count decisions and
cross-check error; the rational masses sum exactly to one.

Expected predictive-loss differences compare selected and restricted forecasts
fitted to the same calibration count and scored on a new process observation.
Cellwise accumulation preserves rare tails that subtraction of large aggregate
losses could lose. A Monte Carlo confidence interval is inappropriate here.

## Conditional target versus enacted policy

The exhaustive calculation conditions on effective access and the admitted batch
size. It excludes action probability, access failure, history and expenditure.
The repeated-policy experiment includes those mechanisms and uses independent
paired replicates. Their targets and denominators are different.

Current process probabilities, selection regions and rare adverse outcomes are
generated in [the manuscript](../output/reports/manuscript.md),
[the exact record](../output/data/exact_decision.json) and the executable companion.
A finite seeded run with no selections cannot establish universal retention.

## Acceptance and interpretation

The exact-decision gate recomputes the entire record from preserved GNN inputs.
Tests exercise rational count masses, independent likelihood inequalities, a
small hand-worked example, altered model files, policy-parameter invariance,
invalid processes and forged saved results. The figure distinguishes evidence
decisions from process probability mass.

This characterizes an authored finite menu. It is neither human parameter
recovery nor evidence of realization. The
[identification discussion](manuscript/supplement.md#sec-empirical) preserves
value/cost confounding and the need for competing-model recovery.
