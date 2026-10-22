# Selection, scoring and rare-event interpretation

Targeted primary-source check completed on 2026-10-19 for the visualization and scholarship revision. This note proposes integrations; it does not certify their adoption or independently review the resulting manuscript. It adds no numerical result, experiment or bibliography entry. The existing `gneiting2007` key supplies the central methodological support.

## Verified sources and access ceilings

**Gneiting and Raftery (2007).** Fresh author-hosted [full text](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf) inspected at p. 359, introduction; p. 363, Examples 1 and 3; and p. 372, Section 7.1, equations 50–53. Strict propriety concerns expected score, with the true distribution uniquely optimal. The paper uses maximized rewards; this project uses minimized losses. Calibration concerns forecasts together with outcomes, whereas sharpness concerns forecast concentration. Its evidence discussion integrates likelihood over the prior and also expresses evidence through sequential prediction. These connections do not identify a score on a new observation with the evidence accumulated over the calibration batch.

**Kass and Raftery (1995).** Fresh [full text hosted at the coauthor's institution](https://sites.stat.washington.edu/courses/stat527/s13/readings/KassRaftery_jasa1995.pdf) inspected at pp. 776–777, Sections 3.1–3.2. Marginal likelihood averages over the parameter prior rather than maximizing likelihood. Bayes factors multiply prior model odds to obtain posterior model odds; the factor alone is not a posterior probability. The sequential predictive interpretation on p. 777 provides corroboration for Gneiting and Raftery. This source is not currently in the bibliography, and adding it is unnecessary for the proposed integration. The author's CMU PDF endpoint returned a browser internal error; the UW PDF was successfully retrieved and read.

**Brier (1950).** The publisher search result confirms the existing bibliographic identity, but the fresh publisher full-text attempt failed with HTTP 403. No new full-text-reading claim or access upgrade is justified. The quadratic score's formula and historical attribution were checked directly in Gneiting and Raftery's Example 1. Existing `brier1950` can remain the historical citation without pretending it supplies a newly inspected reliability decomposition.

**Murphy (1973).** The [publisher abstract](https://journals.ametsoc.org/configurable/content/journals%24002fapme%24002f12%24002f4%24002f1520-0450_1973_012_0595_anvpot_2_0_co_2.xml) identifies uncertainty, reliability and resolution as separate terms of the Brier partition. Full text was not obtained here. Do not add a detailed decomposition, numerical reliability estimate, or full-read catalog status on that basis. The manuscript's existing caution that Brier loss does not isolate calibration remains appropriate.

## Proposed integration

### Explain the two predictive questions

**Placement:** [Exact evidence methods](manuscript/supplement.md#sec-exact-method), after the nested-evidence identity, with a short connection from [main practice Results](manuscript/manuscript.md#sec-main-practice).

**Proposed prose:** Evidence compares prior-averaged predictions for the calibration batch. Although marginal evidence has a sequential predictive interpretation, our assessment instead scores the fitted forecast on new observations. The two criteria therefore answer related but different questions: which declared family better anticipated the batch, and how the selected forecast predicts the next outcome [@gneiting2007].

**Ceiling:** This is an application of the cited framework to the project's declared protocol. It does not claim that Bayesian evidence lacks predictive meaning, that held-out assessment is automatically unbiased under every design, or that the selected family must minimize future loss.

### Explain what propriety promises

**Placement:** [Score definitions](manuscript/supplement.md#sec-scores).

**Proposed prose:** Strict propriety makes truthful probabilities optimal in expectation; it does not guarantee that each finite forecast comparison favors the better distribution. Lower entropy measures concentration and cannot by itself establish accurate prediction [@gneiting2007].

**Ceiling:** Avoid claiming that a lower mean Brier loss proves improved calibration. Do not label posterior entropy as a reliability measure. The manuscript's losses target different random variables, so their numerical magnitudes should not be compared as if they shared a scale.

## Figure interpretation from the declared equations

The following recommendations come from inspection of this project's [exact-selection equation](manuscript/supplement.md#eq:exact-selection) and [risk equation](manuscript/supplement.md#eq:exact-risk), rather than a new empirical finding or a claim attributed to the papers:

- Label the count axis with its event definition and batch size. A decision boundary is a property of the rule; the probability mass over counts depends on the generating process.
- Preserve small positive masses visibly. A logarithmic probability axis or explicitly labeled tail panel can reveal values compressed against zero on a linear axis. A logarithmic display must identify its scale and handle exact zeros explicitly.
- Distinguish a process probability that the rule selects the open family from the posterior probability of a family given a realized batch. They condition in opposite directions and answer different questions.
- Keep the conditional denominator visible: an effective inquiry has already occurred. A selection probability from the oracle is not the unconditional action rate of the repeated policy.
- Selection and subsequent expected loss need separate labels. A rare adverse selection remains possible even when none occurs in a particular seeded run. Its predictive consequence depends on both its mass and its loss difference.

These observations support a more legible exact-decision figure and a clearer caption without a new result or new literature claim. The adopted plotting change still requires export, final-placement inspection and independent review by the coordinating author.

## Retrieval and verification evidence

Raw evidence is retained outside the checkout under the task's GitVault evidence directory, `Local/tmp/tfn-visual-scholarship-20261019/research/`. The directory contains fresh source PDFs, `pdftotext -layout` extracts, a retrieval receipt and verification output. Failed access is recorded separately from successful reading. PDF identity was checked through title, authors and inspected sections, not merely HTTP success.

| Scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| Primary full-text access | `curl --fail --location --show-error --silent` at the two successful URLs above | PDF files retrieved; digest bound to receipt | `gneiting2007.pdf`, `kass1995.pdf`, `retrieval.json` |
| Inspect source identity and passages | `pdftotext -layout`; targeted text searches and page reading | Titles, author names, score examples and evidence section present | `gneiting2007.txt`, `kass1995.txt`, `verification.txt` |
| Reject a false identity marker | Search the Gneiting extract for an intentionally false article title | False marker absent; real title present | `verification.txt` |
| Citation and target closure | Inspect the existing bibliography and manuscript IDs | `gneiting2007` and all proposed local targets exist | `verification.txt` |

These are provenance and document checks. They do not constitute scientific-model validation, a rerun of the numerical experiments, or independent approval of the coordinator's changes.
