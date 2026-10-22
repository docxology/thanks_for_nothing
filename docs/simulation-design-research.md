# Simulation design, precision and structural stress tests

Research dossier, 19 October 2026. This is a methodological handoff, not a report of new experimental results. Only this dossier and research evidence were authored in this pass. The manuscript, catalog, GNN declarations, experiments and figures remain the integrating owner's responsibility.

## Verified source readings

Full bodies were acquired from Europe PMC, PMC or author-hosted copies. Publisher-deposited Crossref metadata was freshly retrieved for all four sources. The external receipt root is `Local/tmp/tfn-experiment-review-20261019/research/` relative to the mounted GitVault root; `retrievals.json` records URLs, actual UTC start/completion times, status, byte size and SHA256. Local text filenames below resolve there. Existing reports were used for navigation, not as proof of source content. No full publisher body was added to the repository.

### Morris, White and Crowther (2019): strengthen an existing citation

[Primary article](https://doi.org/10.1002/sim.8086); [fresh full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6492164/fullTextXML). **Identity:** *Statistics in Medicine* 38(11), 2074–2102; existing key `morris2019`.

**Read:** §3.2, XML `sim8086-sec-0005`; §4.3, `sim8086-sec-0013`; §5.2 and Table 6, `sim8086-sec-0016`/`sim8086-tbl-0006`; §5.3 and equation (1), `sim8086-sec-0017`/`sim8086-disp-0002`; §6.2, `sim8086-sec-0021`. Extraction: `morris2019.txt`, lines 126–148, 309–312, 348–418, 482–515, 534–548.

**Findings:** Crossed generating factors expose interactions that baseline-only changes can miss. Matched generated data improve comparisons. Monte Carlo SE describes finite-repetition error; sample size should follow precision of important performance measures. For binary coverage with anticipated probability p and required MCSE e, equation (1) gives R = p(1−p)/e². The worst-case p = 0.5 is conservative. Precision controls displayed digits; plots can show Monte Carlo uncertainty directly.

**Ceiling:** These recommendations do not validate this implementation, specify human-trial power, or justify an arbitrary cohort increase. A larger sample from one generating mechanism does not explore another mechanism.

**Focused prose:** “We distinguish the generating scenario, target contrast, independent replication unit and performance measure. Replication budgets are assessed against Monte Carlo precision, and crossed scenarios examine interactions that a single baseline cannot characterize [@morris2019].”

### Koehler, Brown and Haneuse (2009): precision beyond a visual plateau

[Primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3337209/); [DOI](https://doi.org/10.1198/tast.2009.0030). **Identity:** *The American Statistician* 63(2), 155–162; proposed key `koehler2009`.

**Read:** §2/§2.1, HTML `P7`–`P10`/`FD1`; §3, `P18`; §4, `P22`; §4.1, `P23`–`P27`; §4.2, `P31`–`P33`; §4.3, `P34`–`P36`/`FD14`. Extraction: `koehler2009.txt`, lines 1063–1079, 1337, 1589–1683. The HTML mathematics retains square roots that plain-text extraction drops; read the equations in HTML alongside the text.

**Findings:** Monte Carlo error is variability across hypothetical repetitions of the same design. A visually stable running estimate supplies no error estimate by itself. Precision depends on both target and generating distribution. The article separates R generated replicates from B bootstrap resamples used to estimate their Monte Carlo error; finite B adds another numerical approximation. Its asymptotic planning relation uses R to the power −1/2 and is approximate.

**Ceiling:** Neither asymptotic scaling nor a pilot estimate guarantees precision in an unseen rare tail. Nested prefixes are correlated checks, not independent replications of the whole experiment. Stabilization cannot validate the fixed model.

**Focused prose:** “Running estimates and Monte Carlo SE are reported together. Increasing bootstrap draws refines a conditional resampling calculation; it does not create additional independent simulated units. Apparent convergence is conditional on the specified generating design [@koehler2009].”

### Saltelli and Annoni (2010): interaction-aware sensitivity

[Author-hosted published article](https://www.andreasaltelli.eu/file/repository/PublishedPageNumbers.pdf); [DOI](https://doi.org/10.1016/j.envsoft.2010.04.012). **Identity:** *Environmental Modelling & Software* 25(12), 1508–1517; proposed key `saltelli2010`. The full paper has two authors; a similarly titled conference item should not supply its author list.

**Read:** §2, printed pp.1509–1510; §3, p.1510; §5.1, p.1511, Figure 2 and equations (1)–(2). PDF file has an introductory cover, so printed p.1509 is PDF page 3. Extraction: `saltelli2010.txt`, lines 111–198, 201–251, 295–358.

**Findings:** Changes along single-factor directions leave interactions untested. Local sensitivity can be informative near its baseline, but broad robustness claims require stronger assumptions or broader exploration. The paper demonstrates crossed two-level contrasts and discusses alternatives that examine more of the input space.

**Ceiling:** This does not require every plot to be nonlinear, forbid a scientifically justified local derivative, or establish that any chosen parameter ranges are plausible. A crossed finite grid supports conclusions on that grid; it is not automatically a variance-based global sensitivity analysis or a test of all model structures.

**Focused prose:** “Sensitivity contrasts vary selected factors jointly and report their admitted ranges. Baseline derivatives and one-factor slices retain their local interpretation. Structural alternatives are assessed separately from precision within a fixed model [@saltelli2010].”

### Hanley and Lippman-Hand (1983): distinguish unsampled events from impossible events

[Author-hosted full text](https://jhanley.biostat.mcgill.ca/c607/ch08/zero_numerator.pdf); [publisher identity](https://jamanetwork.com/journals/jama/article-abstract/385438). **Identity:** *JAMA* 249(13), 1743–1745; DOI `10.1001/jama.1983.03330370053031`; proposed key `hanley1983`.

**Read:** author retypeset PDF page 2, “Making Inferences: The Rule of Three,” equation (1); page 3, Table 2 and “Comment.” Extraction: `hanley1983.txt`, lines 55–128. This copy has four retypeset pages; do not map those page numbers directly to the three journal pages.

**Findings:** A zero observed numerator leaves a positive upper bound on the event probability. Solving (1−p)^n = 0.05 gives the exact one-sided 95% upper endpoint 1−0.05^(1/n); 3/n approximates it. The denominator remains essential to interpreting zero observations.

**Ceiling:** Applying this binomial result requires independent Bernoulli units sharing an event probability. Dependent adaptive windows are not interchangeable units. This bound neither proves a mechanism-exact zero nor replaces an available exact probability for the same target.

**Focused prose:** “Zero observed events are reported with their independent denominator and, where the binomial assumptions apply, an upper probability bound. Exact structural impossibility, exact positive rare-event probability and finite-sample non-observation remain distinct [@hanley1983].”

## Application to this repository: proposed design, not completed results

The following operational choices are this dossier's recommendations, not additional claims extracted from the papers.

| Quantity | Independent unit and uncertainty | Required reporting distinction |
|---|---|---|
| Mean paired policy contrast | Whole simulated agent or replicate, paired across policies; retain complete vectors within fixed strata | Repeated windows, fixation sites and contrast columns do not increase the independent unit count |
| Fresh-outcome predictive assessment | Assessment outcomes within a trained replicate; averaging more outcomes changes conditional evaluation noise | Assessment draws do not substitute for independent agents; preserve the outer replicate when estimating between-unit uncertainty |
| Bootstrap endpoint or maximum-root quantile | Resamples conditional on the retained unit vectors | Report resampling budget and conditional numerical uncertainty separately from the outer cohort |
| Coverage or interval availability | Independent complete simulated datasets/experiments, each yielding one success indicator | This count is separate from the independent units inside each dataset; unavailable intervals must retain their declared denominator treatment |
| Conditional exact evidence decision | Exhaustive calibration counts under specified process probability, batch size and effective access | No Monte Carlo interval for an exactly enumerated probability; numerical display precision is a different matter |
| Repeated enacted-policy revision | Independent full trajectories incorporating activity, access, prior history and expenditure | Conditional exact-selection probability cannot be relabeled as the marginal trajectory revision probability |

For a paired mean, use a pilot estimate of the SD of the **whole-unit differences**, not the marginal SDs of two unpaired arms, when planning precision. For fixed strata with independent sampling, the variance of the weighted mean is the sum of squared stratum weights times within-stratum mean variances. Record the weighting target explicitly. A prefix ladder should report unique independent units, MCSE and the full-budget estimate; its overlapping prefixes do not constitute separate replications. A fresh independent seed series can test stability without that overlap, but any stopping or tolerance rule must be stated.

Precision requirements must be interpretable for each endpoint: nats per assessed outcome, Brier units, probabilities or expenditures. No universal increase in N is prescribed. If a chosen budget misses the target, report that shortfall. Preserve genuine unavailable rare-event intervals instead of converting an empirical constant into certainty. An exact oracle can make a vast Monte Carlo expansion unnecessary for its own conditional target.

Crossed sensitivity can prioritize scientifically distinct mechanisms: observation reliability with prior support; action cost with access probability; assessment regime with policy; and world weighting with the contrast target. Use only admissible declarations, make zero-support and label-equivalent scenarios explicit structural alternatives, and distinguish numerical-budget changes from changes to the model. A two-factor interaction contrast is the difference between the factor-A effects at two factor-B settings. It is meaningful only with compatible targets and declared values. A mechanism identity that holds throughout the admitted domain needs a proof/control, not a search for a nonzero visual effect.

## Figure interpretation and inspection handoff

This pass establishes interpretation criteria; it does **not** claim manual inspection of the final figure set. The integrating owner must inspect every rendered figure and connect each judgment to its source records.

| Suspicious appearance | Legitimate explanation to test | Figure response |
|---|---|---|
| Straight line | An authored affine scoring/valuation rule, exact mixture relation or displayed interpolation | State the equation/domain; show evaluated points; label interpolation. Expose a distinct stochastic or interaction target if that is the scientific question |
| Flat zero with no interval | An independently checked mechanism identity, or an empirical sample constant | Distinct exact/unavailable symbols; never add jitter, fabricated variance or forced effects |
| No revision events | Rare positive probability missed in a finite run, or true impossibility | Show observed count/denominator and relevant exact conditional probability; qualify their different targets |
| Very narrow interval | Large independent cohort, low paired variance, averaging, wrong denominator or lost floating-point variation | Inspect whole-unit differences, dependence, cancellation controls and numerical scale; keep a readable common view plus a labeled detail panel |
| Smooth apparent convergence | Correlated prefixes or a genuinely stable mean | Display unique N and MCSE; do not infer independent confirmation from successive prefixes |
| Similar policies | Observational equivalence, shared support or weak discriminating observations | Retain the null; use a structural contrast only when it changes an admissible scientific assumption |

These checks address whether the picture communicates the declared computation. They do not establish gratitude efficacy, human metacognitive sensitivity, clinical benefit or realization of emptiness.

## Citation records for selective integration

The first entry already exists. Koehler supplies the most direct additional precision source; Hanley supplies the zero-count distinction; Saltelli is useful if the revision makes interaction or robustness claims. Lakens was not added: these simulation-specific sources directly address the current target, without importing a human-study sample-size rationale.

```bibtex
@article{morris2019,
  author = {Morris, Tim P. and White, Ian R. and Crowther, Michael J.},
  title = {Using simulation studies to evaluate statistical methods},
  journal = {Statistics in Medicine},
  year = {2019}, volume = {38}, number = {11}, pages = {2074--2102},
  doi = {10.1002/sim.8086}
}
@article{koehler2009,
  author = {Koehler, Elizabeth and Brown, Elizabeth and Haneuse, Sebastien J.-P. A.},
  title = {On the Assessment of Monte Carlo Error in Simulation-Based Statistical Analyses},
  journal = {The American Statistician},
  year = {2009}, volume = {63}, number = {2}, pages = {155--162},
  doi = {10.1198/tast.2009.0030}
}
@article{saltelli2010,
  author = {Saltelli, Andrea and Annoni, Paola},
  title = {How to avoid a perfunctory sensitivity analysis},
  journal = {Environmental Modelling \& Software},
  year = {2010}, volume = {25}, number = {12}, pages = {1508--1517},
  doi = {10.1016/j.envsoft.2010.04.012}
}
@article{hanley1983,
  author = {Hanley, James A. and Lippman-Hand, Abby},
  title = {If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators},
  journal = {JAMA},
  year = {1983}, volume = {249}, number = {13}, pages = {1743--1745},
  doi = {10.1001/jama.1983.03330370053031}
}
```

Hanley's Crossref response contains only Hanley and the first page. The author PDF header and publisher citation identify both authors and the complete page range. Publisher direct retrieval returned 403; the separately retained `web.run` response supplied the readable publisher identity. Koehler's Europe PMC XML route returned 500, while PMC HTML contained the article body and citation metadata. Failed routes remain in the receipts and were not counted as full-text readings. The extraction helper initially failed on an untitled XML section; it was corrected to retain an explicit untitled label and rerun successfully.

## Evidence and verification

Repository evidence: `.omo/evidence/simulation-design-research/`. External full texts, extracted text, retrieval receipts and verifier: `Local/tmp/tfn-experiment-review-20261019/research/`. `verification.json` captures positive source identity, a deliberately swapped source-identity rejection, incomplete-metadata detection, source hashes/byte counts, locator checks and numerical known-answer checks. `verification.log` records the invocation outcome. These checks qualify the research handoff, not the project's simulations or release gates.
