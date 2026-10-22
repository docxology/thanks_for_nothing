# Targeted scholarship and inference design for v0.6.0

Research date: 2026-10-15 (America/Los_Angeles; retrieval receipts use UTC). Baseline: private Thanks for Nothing commit `fa237e544d445ac81b4420bd86b59fb34445dfae`, v0.5.0. This dossier supplies five focused additions and proposed manuscript changes. It does not certify the subsequent implementation, statistical coverage, manuscript render or release. No publication or DOI action was performed.

The complete manuscript and existing scholarship/research dossiers were read, with particular attention to the eight primary hypotheses, sixteen transfer contrasts, forty-two active-policy contrasts, independent assessment and the distinction between appreciation, access, revision and realization. Existing dossier results were treated as historical reports, not rerun evidence. Fresh observations here concern the source texts and metadata below. Source receipts, extraction outputs, failed responses and verification artifacts are under `/Volumes/GitVault/Local/evidence/thanks-for-nothing-v060-20261015/research/` (called the **receipt root** below).

## Five primary-source additions

### Romano and Wolf: joint resampling, with explicit assumptions

**Identity:** Joseph P. Romano and Michael Wolf (2005), “Exact and Approximate Stepdown Methods for Multiple Hypothesis Testing,” *Journal of the American Statistical Association* 100(469), 94–108. [DOI 10.1198/016214504000000539](https://doi.org/10.1198/016214504000000539).

**Access:** [Author institutional published PDF](https://www.econ.uzh.ch/dam/jcr%3Affffffff-935a-b0d6-ffff-ffffd823d949/jasa.pdf), targeted reading of introduction, §4.2, printed pp. 102–103, Assumptions B1–B2, Theorems 6–7 and Remarks 4–8. Receipts: `romano2005.pdf`, `.txt`, `-crossref.json`.

**Support:** Centered joint bootstrap distributions can supply maximum-statistic critical values. The asymptotic argument requires appropriate joint bootstrap consistency and a nondegenerate limiting law with continuity conditions. The two-sided construction uses absolute deviations. Studentization is discussed separately; this is not a universal finite-sample guarantee.

**Placement and ceiling:** Cite in `sec-statistics` for the joint-bootstrap lineage. Name the proposed implementation a single-step standardized bootstrap rectangle, not Romano–Wolf stepdown: the latter's sequential algorithm is not being implemented. Citation does not establish coverage for these project contrasts.

### Hothorn, Bretz and Westfall: simultaneous intervals and covariance

**Identity:** Torsten Hothorn, Frank Bretz and Peter Westfall (2008), “Simultaneous Inference in General Parametric Models,” *Biometrical Journal* 50(3), 346–363. [DOI 10.1002/bimj.200810425](https://doi.org/10.1002/bimj.200810425).

**Access:** [University of Munich author technical report 019](https://epub.ub.uni-muenchen.de/2120/1/tr019.pdf), dated 2008-02-15; §§2–3, report pp. 2–6, especially covariance assumptions and common critical values. Journal identity is independently verified through Crossref; final journal full-text layout was not inspected. Receipts: `hothorn2008.pdf`, `.txt`, `-crossref.json`.

**Support:** Simultaneous inference uses the joint covariance of contrasts; standardized inference assumes positive marginal variances. Single-step intervals share a critical value. The general normal approximation is asymptotic unless a specific exact model applies.

**Placement and ceiling:** Use beside the distinction between pointwise and simultaneous uncertainty, not as a theorem about this nonparametric implementation. The inspected report's p. 5 confidence-level expression is inconsistent with its adjacent critical-probability expression; do not copy that display. Specify the target maximum-root probability directly.

### Kobayashi and Hsu: information demand has competing motives

**Identity:** Kenji Kobayashi and Ming Hsu (2019), “Common neural code for reward and information value,” *PNAS* 116(26), 13061–13066. [DOI 10.1073/pnas.1820145116](https://doi.org/10.1073/pnas.1820145116).

**Access:** [Author laboratory PDF](https://neuroecon.berkeley.edu/public/papers/PNAS%202019%20Kobayashi.pdf), article pp. 2–3 Results (“Information Seeking Is Sensitive to Instrumental Benefits”; “Coexistence of Instrumental and Noninstrumental Motives”), pp. 5–6 Discussion and behavioral methods. Supplement and raw data were not inspected. Receipts: `kobayashi2019.pdf`, `.txt`, `-crossref-retry.json`.

**Support:** Participants could purchase information before revising lottery choices. The comparison included instrumental value, fixed/entropy bonuses and anticipatory utility; the combined anticipatory account improved behavioral prediction in this task. The discussion explicitly leaves room for bonus motives in other settings.

**Placement and ceiling:** In `sec-practice-model` and `sec-limitations`, distinguish the stipulated opportunity bonus from forward-looking instrumental value and favorable anticipation. Neither the neural title nor the behavioral model comparison validates a gratitude parameter, the project's information bonus or an emptiness mechanism. No neural inference is proposed here.

### van Lieshout and colleagues: costly curiosity, with a nontrivial outcome definition

**Identity:** Lieke L. F. van Lieshout, Annelinde R. E. Vandenbroucke, Nils C. J. Müller, Roshan Cools and Floris P. de Lange (2018), “Induction and Relief of Curiosity Elicit Parietal and Frontal Activity,” *Journal of Neuroscience* 38(10), 2579–2588. [DOI 10.1523/JNEUROSCI.2816-17.2018](https://doi.org/10.1523/JNEUROSCI.2816-17.2018).

**Access:** [PMC full article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6705901/), Participants; behavioral Procedures/Analysis for Experiments 1–2; Behavioral Results 1–3; Discussion “Curiosity is modulated by OU.” Receipts: `vanlieshout2018.html`, `-readable.txt`, `-crossref.json`.

**Support:** In Experiment 2, participants could incur an extra 3–6 seconds to learn a lottery outcome without changing its payout. Waiting increased with the study's uncertainty predictor. That predictor multiplied Shannon entropy by the difference in outcome payoffs; it was not pure entropy. Expected value also influenced explicit curiosity in Experiment 3.

**Placement and ceiling:** Add to the empirical bridge in `sec-limitations`: information demand can be measured beyond verbal endorsement. This task does not identify revisability, gratitude or contemplative inquiry; its predictor cannot be equated with the project's candidate information gain.

### DeSteno and colleagues: patience is both a bridge and a rival explanation

**Identity:** David DeSteno, Ye Li, Leah Dickens and Jennifer S. Lerner (2014), “Gratitude: A Tool for Reducing Economic Impatience,” *Psychological Science* 25(6), 1262–1267. [DOI 10.1177/0956797614529979](https://doi.org/10.1177/0956797614529979).

**Access:** [Author-hosted Harvard accepted manuscript](https://jenniferlerner.com/wp-content/uploads/2017/07/7.Gratitude.pdf), manuscript pp. 7–12: Method, manipulation checks, temporal discounting and Discussion. The cover identifies the published DOI; Crossref splits the title/subtitle. Supplement and participant data were not inspected. Receipts: `desteno2014.pdf`, `.txt`, `-crossref.json`.

**Support:** Seventy-five young adults were randomly assigned gratitude, happiness or neutral autobiographical recall, followed by incentivized intertemporal choices. The planned gratitude-versus-pooled-comparators contrast favored greater patience. This is not proof of every separate pairwise contrast or lasting adherence.

**Placement and ceiling:** Add after costly helping in `sec-social-gratitude`; use in `sec-limitations` to motivate independent measures of patience and inquiry. An effect on willingness to wait could reflect altered delay valuation rather than increased value of examinability. No gratitude-to-realization result follows.

## Proposed simultaneous procedure: precise scope and unresolved risks

The following is a project-specific statistical proposal informed by the two methods sources above, not an extracted theorem or a claim that implementation has passed. The root integrator selected original-standard-error normalization rather than the existing resample-studentized bootstrap t.

Let the family contain all 58 fixed, already-reported gaze contrasts. Transfer data form five fixed-world blocks, each containing a complete paired-agent vector across bridges, conditions and endpoints. Active data form two independent context blocks, each containing a complete vector of the replicate's three-window averages across policies and endpoints. In the inspected baseline, `gaze_active.py::build_active_gaze` seeds with context index as well as replicate/window; matching replicate numbers across contexts therefore does not establish a common experimental unit.

For each bootstrap draw:

1. Draw agent indices independently within each transfer world; use the same selected indices for every transfer column in that world. Retain fixed equal world weights.
2. Draw replicate indices independently for each active context; share its indices across that context's endpoint/contrast vector. Do not pair two contexts merely because both use replicate integers 0–63.
3. Recompute the complete 58-vector of means. For each admitted stochastic column, form `Z*_j = (theta*_j - theta_hat_j) / SE_hat_j`, using the **original** standard error throughout. Set `M* = max_j abs(Z*_j)`.
4. Estimate the 0.95 quantile `c` of the joint maxima under a declared finite-draw quantile convention. Report `theta_hat_j ± c SE_hat_j`. Keep all existing percentile, bootstrap t and analytic pointwise intervals separately.

This plug-in standardization is distinct from bootstrap t, whose denominator changes in every resample. Under regular finite-variance, positive-variance and consistent joint-bootstrap conditions, an original consistent normalization can support an asymptotic rectangle. These conditions do not supply a finite-n 95% guarantee. A statistic based on raw, uncentered resample means would instead conflate observed effects with estimation error. Independently resampling each contrast would erase shared-unit dependence. Standardization makes probability, loss and movement endpoints commensurable for the maximum without changing their displayed units.

| Boundary | Required handling | Failure to avoid |
| --- | --- | --- |
| Declared family | One joint family includes both transfer and active blocks in each draw; retain ordered contrast identity | Two separate 95% families described as joint 95% coverage over all 58 |
| Mechanism-backed identity | Declare exact transfer valuation and active sham identities from executable contracts and reject any violated identity | Inferring a deterministic null solely because the observed sample is constant |
| Other zero-variance sample | Mark its stochastic interval unavailable and full-family coverage status partial/unavailable; list the covered stochastic subset | Zero-width interval advertised as evidence of population equality |
| Empty stochastic subset | Report exact identities and unavailable columns without inventing a maximum or bootstrap critical value | Returning a numerical critical value from an empty family |
| Resample degeneracy | With original-SE normalization, resample SE is not a denominator; original SE must still be positive | Calling this behavior bootstrap-t failure handling or borrowing its guarantee |
| Linear dependence | Preserve duplicated/opposite columns and shared controls; a maximum need not invert covariance | Adding arbitrary jitter or dropping comparisons to force full rank |
| Monte Carlo quantile error | Retain a conditional binomial order-statistic bracket for the chosen bootstrap quantile, with ties and finite-rank endpoints handled explicitly | Treating the quantile bracket as sampling-coverage proof or silently substituting its upper endpoint |
| Exploratory origin | State that the analysis was chosen after examining v0.5 results | Calling multiplicity adjustment preregistration or converting it into confirmatory human evidence |

The rare stationary selection already exposed by the manuscript is a concrete warning: an observed all-zero sample need not describe a zero-probability mechanism. The family status must remain honest even if removing such a column would improve the apparent coverage or visual result.

The Monte Carlo bracket concerns random bootstrap draws **conditional on the observed data and procedure**. It does not quantify uncertainty about model adequacy or whether the rectangle has its nominal repeated-sample coverage. Discrete roots and tied quantiles require conservative order-statistic treatment; unbounded order-statistic endpoints must remain visible when the draw budget cannot identify a requested bracket. If an implementation uses an upper bracket endpoint to construct intervals, that is a distinct declared procedure requiring its own evaluation.

Suggested finite fixtures are independent Gaussian columns, strongly correlated/opposite/duplicate columns, unequal-variance fixed strata, centered skewed columns and a rare-event sample-constant case. Every fixture needs an independently known population mean vector. Count a repetition as successful joint coverage only if every required stochastic target is covered and all required intervals are available; report availability separately. Add a deliberate pointwise-only comparator and pairing-disruption control so that a test can reveal the errors it purports to detect. Coverage rates need binomial uncertainty and preserved unfavorable outcomes. These are proposed acceptance scenarios, not results recorded by this researcher.

## Sharper empirical bridge and manuscript integration

The baseline already rejects a shortcut from a software score to realization. The substantive improvement is to turn “generic curiosity” into several discriminating alternatives, rather than merely listing it as a rival label. The following design deductions are this project's synthesis of the inspected sources.

| Proposed manipulation or measure | Distinction it can test | Observation that would constrain the thesis |
| --- | --- | --- |
| Appreciation of enabling conditions versus matched pleasant-event and neutral activities | Added motivational orientation beyond affect and engagement | Only positive-language ratings change |
| Real availability versus a declared unavailable alternative, with recognition/comprehension probes | Objective access versus noticing and using access | Choices change without participants recognizing the alternative |
| Useful versus noninstrumental information at matched uncertainty | Instrumental improvement versus information demand for its own sake | Apparent appreciation effect is fully explained by expected task benefit |
| Favorable versus unfavorable information with usefulness held comparable | Examinability versus anticipated pleasant information | Inquiry rises only for welcome conclusions |
| Delay, effort and monetary costs varied separately | Patience versus willingness to bear an inquiry cost | Increased waiting disappears after accounting for delay preference and does not generalize to other costs |
| Stable useful representations versus genuinely contradicted ones | Appropriate retention/revision versus compliance with a request to change | Accurate beliefs weaken indiscriminately |
| Later independent predictions and retention of alternatives | Finite consequence and continuing revisability | Better immediate selection fails to improve independent prediction or alternative availability |

This is a future human-study design, not an experiment executed here. It must not turn every proposed contrast into an undeclared efficacy endpoint. Prespecify the estimand, primary comparison and meaningful outcome, and use separate construct/process measures. Model-recovery and parameter-recovery requirements already cited in the manuscript still apply. Cost, action precision and opportunity value remain confounded unless the design supplies independent variation; adding information choices alone does not solve that identification problem.

The stronger Realizing Emptiness connection remains **continued availability of alternatives and conditional use of representations**, already supported by the manuscript's bounded source reading. Additional curiosity and patience papers sharpen tests of the appreciation-to-action link; they do not increase the philosophical evidence ceiling. A person can seek information, tolerate delay and switch predictors while still treating the winning description as intrinsically established.

Suggested short insertion at `sec-practice-interpretation`:

> The preference for examinability has several behavioral alternatives. Information can be useful for a later decision, attractive because of anticipated favorable content, or worth a delay even when it cannot alter a payoff. An appreciation-induced increase in waiting can also reflect patience. A specific mechanism therefore requires selective effects on inquiry under matched information usefulness, content and costs, followed by evidence-responsive retention or revision and independent assessment.

Use the three empirical additions as citations near their specific premises, while marking the final design sentence as the manuscript's proposal. At `sec-statistics` and `supp-gaze-intervals`, add the exact simultaneous procedure only after execution and verification. Revise blanket statements such as “all estimation intervals are pointwise” to identify their actual scope if the new family is admitted. Keep the original eight-test Holm family unchanged. In gaze figure captions, distinguish pointwise intervals, simultaneous intervals, mechanism identities and unavailable entries explicitly; avoid reusing one legend symbol for all four.

## Bibliography recommendations

These entries are recommendations for the manuscript owner; this worker did not edit the bibliography or source catalog. Use `full_text_targeted_sections` with the exact version/access note above, not an unqualified “full article verified” claim. Framework/methods sources establish their own proposals and assumptions, not empirical gratitude effects.

```bibtex
@article{romano2005,
  author = {Romano, Joseph P. and Wolf, Michael},
  title = {Exact and Approximate Stepdown Methods for Multiple Hypothesis Testing},
  journal = {Journal of the American Statistical Association},
  year = {2005}, volume = {100}, number = {469}, pages = {94--108},
  doi = {10.1198/016214504000000539}
}
@article{hothorn2008,
  author = {Hothorn, Torsten and Bretz, Frank and Westfall, Peter},
  title = {Simultaneous Inference in General Parametric Models},
  journal = {Biometrical Journal},
  year = {2008}, volume = {50}, number = {3}, pages = {346--363},
  doi = {10.1002/bimj.200810425}
}
@article{kobayashi2019,
  author = {Kobayashi, Kenji and Hsu, Ming},
  title = {Common neural code for reward and information value},
  journal = {Proceedings of the National Academy of Sciences},
  year = {2019}, volume = {116}, number = {26}, pages = {13061--13066},
  doi = {10.1073/pnas.1820145116}
}
@article{vanlieshout2018,
  author = {van Lieshout, Lieke L. F. and Vandenbroucke, Annelinde R. E. and M{\"u}ller, Nils C. J. and Cools, Roshan and de Lange, Floris P.},
  title = {Induction and Relief of Curiosity Elicit Parietal and Frontal Activity},
  journal = {Journal of Neuroscience},
  year = {2018}, volume = {38}, number = {10}, pages = {2579--2588},
  doi = {10.1523/JNEUROSCI.2816-17.2018}
}
@article{desteno2014,
  author = {DeSteno, David and Li, Ye and Dickens, Leah and Lerner, Jennifer S.},
  title = {Gratitude: A Tool for Reducing Economic Impatience},
  journal = {Psychological Science},
  year = {2014}, volume = {25}, number = {6}, pages = {1262--1267},
  doi = {10.1177/0956797614529979}
}
```

## Access failures and evidence ledger

Initial Europe PMC XML attempts for Kobayashi and van Lieshout returned small error bodies, preserved as `kobayashi2019.xml` and `vanlieshout2018.xml`; they are not admitted full text. The first Kobayashi Crossref response was empty; the encoded-DOI retry succeeded. Full text was recovered from the author laboratory PDF and PMC HTML respectively. HTTP headers are preserved with cookie/authentication header fields omitted; no credentials were requested or recorded. `retrievals.json` and `fallback-retrievals.json` retain requested URLs, lengths, hashes and retrieval times. Header files retain response status/final-URL metadata. `verified-sources.json` is a fresh identity/format/locator receipt, not automated semantic validation.

Run the invocations below from the receipt root; commands operate only on these research artifacts. Source downloads used `retrieve.rb` with external TMPDIR; PDF text was extracted with `pdftotext -layout`. HTML text was extracted without executing the page. No Python environment, package installation or manuscript generator was used.

| Criterion / exact scenario | Invocation | Binary observable | Captured artifact |
| --- | --- | --- | --- |
| Five identities and inspected source bodies are present | `ruby verify-research.rb` | exit 0; five DOI/title/body/locator checks pass | `verification-positive.txt`, `verified-sources.json` |
| Failed retrieval cannot masquerade as a paper | `ruby verify-research.rb --pdf kobayashi2019.xml` | exit 1; PDF-magic rejection | `verification-negative.txt`, retained failed `.xml` body |
| Dossier includes five sources, narrow procedure and empirical bridge | `ruby verify-dossier.rb` with the dossier path argument | exit 0; five DOI entries and required sections found | `dossier-verification.txt` |
| Dossier and admitted receipts have recorded nonempty bytes | Same dossier verifier | all required files nonempty and SHA-256 recorded | `artifact-manifest.json` |

The negative control tests the artifact-admission check, not a statistical procedure. Statistical implementation, family coverage, exact-null gates, render QA and source-catalog integration remain the root integrator's work. No success claim for those scenarios is made here.
