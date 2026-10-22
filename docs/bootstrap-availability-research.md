# Bootstrap availability: sources and finite derivation

Reviewed 2026-10-19. This dossier distinguishes inspected source material from
the project's new mathematical control. Current numerical values belong to the
[generated operating checks](manuscript/supplement.md#supp-diagnostics).

## Empirical resampling

Efron, *Bootstrap Methods: Another Look at the Jackknife*, Annals of Statistics
(1979), [DOI](https://doi.org/10.1214/aos/1176344552).
Inspected the [article scan](https://ledaliang.github.io/journalclub/_static/efron1979/Efron1979.pdf),
section 2, printed pages 3-4, equations 2.4-2.8 and the calculation-method list.
The empirical distribution assigns equal mass to observed units; resampling is
independent with replacement. The Bernoulli example makes the conditional
success probability the observed fraction. Direct calculation and Monte Carlo
approximation are separate ways to evaluate a bootstrap distribution. This
supports the resampling construction, not a universal finite-sample guarantee.

## Failed estimates and denominators

Morris, White and Crowther, *Using simulation studies to evaluate statistical
methods* (2019), [DOI](https://doi.org/10.1002/sim.8086), sections 3.4 and 5.1.
Inspected the published full-text XML retained at
`data/scholarship/receipts/revision/morris2019-fulltext.xml`, sections
`sim8086-sec-0007` and `sim8086-sec-0015`.
SHA256: `c5f525e6e495c17d25bc191c728452377752e4b476e2ef096e5595f9f879f0bd`.
The guidance requires reporting missing estimates and investigating causes and
data dependence. A fallback becomes a different method. Accordingly, this
project retains all-experiment coverage and availability, while describing
conditional coverage with its explicit selected denominator.

Hall (1988), [DOI](https://doi.org/10.1214/aos/1176350933), remains an
abstract-level source here. Its comparison of interval methods does not support
an attributed theorem about this finite discrete fixture or the strict policy.

## New project calculation and scope

Conditional on an original Bernoulli count, a resample is constant only if all
draws are successes or all are failures. Independence across bootstrap draws
gives the probability that no resample is constant. Averaging this quantity over
the original binomial count yields the
[exact availability formula](manuscript/supplement.md#eq:bootstrap-availability).
This is a project derivation under an explicit software policy, not a theorem
attributed to the cited articles. Exhaustive binary-sample and resample-sequence
enumeration checks a small case independently of the closed formula.

For fixed finite sample size, increasing the number of resamples makes the
strict all-positive-variance requirement harder to satisfy. This explains a
procedure-specific availability limit. It neither establishes conditional
coverage nor recommends discarding undefined roots. The annotated calibration
figure preserves the difference between an exact availability benchmark,
observed availability and the coverage of returned intervals.
