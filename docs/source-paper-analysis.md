# Source paper analysis: Computational mechanisms of gratitude practice

This analysis concerns Fisher, Sandved Smith and Hohwy’s [PsyArXiv preprint version 1](https://osf.io/preprints/psyarxiv/xm25y_v1), published 1 November 2025. The archived full text is `data/sources/gratitude_preprint_v1.docx`, SHA256 `f9ba1ed0e3e5ecff219348eccc322a1ee5156d001eba7eff87be91ac01a08e46`. Paragraph identifiers below refer to the preserved paragraph extraction `source-paper.txt` in the external source-recovery evidence directory. They are DOCX paragraph positions, not printed page numbers. The math-aware Pandoc extraction `source-paper.md` was also inspected; these notes do not infer equations from missing image content.

The [journal publication](https://doi.org/10.1162/NECO.a.1591), dated 9 October 2026, has separately verified bibliographic metadata and an inspected abstract. Its full text was not inspected. Therefore every detailed attribution below is to preprint v1; these are not assertions that the journal version retains every wording or implementation detail. The OSF API’s DOI field is null in the saved receipt; the catalog uses the stable version URL rather than an assumed DOI. The OSF license receipt identifies CC BY 4.0.

## What the authors set out to explain

The authors acknowledge mixed intervention evidence (P010, P013), then propose precision allocation to positive observations as a mechanistic account (P017). Their four-stage protocol learns a world model, measures its baseline behavior, applies retrospective positive-event rehearsal, and measures behavior again (Methods, P033–P066). The three principal demonstrations are world-belief change, optimism-task change, and a separate attention proof of concept. These are synthetic agents, not study participants.

The authors intend future optimism-task data to provide an empirical bridge because fitting the continuous daily-life model directly would be difficult (P027, P128). That is a proposed research strategy. The source supplies no fitted human gratitude-intervention dataset establishing that bridge.

## Reconstruction map

| Component | Source locator | Source specification or reported observation | Interpretation limit |
| --- | --- | --- | --- |
| World model | Methods P035–P039 | Two hidden world states; three valenced observations; initially flat state prior; learned likelihood and state prior; environment transition probability determined by “luckiness”; 12 observations per day for seven days; 1000 simulated agents across luckiness levels | The parameter describes an artificial environment, not a human personality or clinical stratum |
| Common-day assessment | P043, P066 | Authors describe all agents receiving the same day, without learning during assessment | A common transition matrix alone does not guarantee identical realized stochastic observations; implementation must verify actual replay |
| Optimism task | P047–P051 | Two hidden-state factors: good/bad life-event outcome and learned going-well/poorly context; context conditions precision; 70 trials; randomly generated initial event beliefs | The task incorporates a valence-sensitive observation model; an updating difference is not independent evidence of well-being |
| Gratitude rehearsal | P060–P062 | Remember three positive time points per day; re-evaluate them with increased precision; assign full going-well confidence at those time points; update the learned likelihood | The certainty assignment is a modeling intervention, not an observed human posterior; behavior when fewer than three positive events occur must be specified in code |
| Attention task | P055–P057, P105 | A valenced 13-location scene, five positive/five negative/three neutral locations; preferences rank positive above neutral above negative; precision is manipulated | A separate manipulated-precision demonstration cannot establish that gratitude learning automatically transfers to gaze |

## Mechanism and mathematical assumptions

In a categorical world model, state inference depends jointly on a prior and a likelihood: the model-relative posterior is proportional to their product. The source’s attention interpretation changes the contribution of positive evidence, then consolidates changed state assignments into learning (P062). It does not observe gratitude directly. In particular, full confidence in “going well” is stronger than merely increasing a finite likelihood precision: finite precision applied to overlapping likelihoods need not produce a posterior probability of exactly one. A corrected experiment should expose whether it uses a finite precision transformation or the source’s stated certainty operation.

Dirichlet concentration parameters, their normalized expected probabilities, and any precision transformation must be recorded separately. Rehearsing a stored event is not the same as collecting a new independent environmental observation. If retrospective assignments replace earlier assignments, the update must specify replacement versus addition and guard against double counting. These are project requirements for a reproducible reconstruction, not claims that the paper states a particular count-update equation.

The preprint describes variational free energy as bounding a gap between model and true generative process (P025). Our mathematical interpretation is narrower: under the usual variational identity, free energy bounds negative log model evidence and differs from it by a posterior KL divergence. This does not supply a bound on an arbitrary discrepancy between a model and the true world. Similarly, expected-free-energy planning in the scene task should not be conflated with state-estimation free energy; the task’s preferences and likelihood precision jointly influence choices (P057). See the [process theory](https://doi.org/10.1162/neco_a_00912), [finite comparison](https://doi.org/10.1162/neco_a_01357) and [POMDP tutorial](https://doi.org/10.1016/j.jmp.2021.102632) for the theoretical lineage, with access limits recorded in the catalog.

## What the preprint reports

Before rehearsal, illustrative agents with low luckiness retain negative world beliefs even in positive states, while high-luckiness examples retain positive beliefs in negative states; the middle example tracks changes more closely (Results P068, Figure 2 caption P072). After rehearsal, low-luckiness examples identify positive states more readily while retaining negative-state responses; the middle example changes its confidence; high-luckiness examples change little or become more consistently positive (P074, Figure 3 caption P077).

The optimism demonstration reports heterogeneous updates, including persistent average pessimistic asymmetry in some low-luckiness agents and stronger changes in intermediate ranges (P079, Figure 4 caption P082; discussion P116). These are the authors’ descriptions of their simulation, not newly reproduced estimates. We do not transcribe graph heights as data, infer uncertainty intervals from plotted points, or treat the synthetic agents as a sample from a human population.

The attention demonstration plots example trajectories and category occupancy before/after the precision manipulation (P103–P105). P105 explicitly identifies that manipulation. Consequently, the strongest supported reading is a proof of concept that different precision settings can alter a policy-driven attention model. The stronger language about automatic habitual change in P108 requires a learned transfer rule and its own test.

## Boundaries that must survive reuse

The source explicitly restricts the world simulation to stable environments with opportunities for good observations and excludes trauma and unstable environments (P035). Its discussion warns that optimism is not adaptive when good opportunities are unavailable or the environment becomes persistently bad (P122). P112 separately recognizes that serious loss may require grief and processing rather than an insistence that things are going well. Those qualifications are part of the model’s scope, not optional caveats.

The preprint sometimes interprets its synthetic optimism variable as well-being or efficacy (P047, P110–P116). We retain these as attributed interpretations rather than adopting them as established outcomes. The simulation has no independent human well-being measure, no clinical trial, no neural recordings, and no measurement of contemplative realization. Even increased positive expectation can be accompanied by worse prediction accuracy or unsafe choices. The corrected experiments therefore need calibration, adverse-environment and outcome-sensitive controls, not merely a positive change score.

Its account of temporal ordering and learning (P118) suggests a testable sensitivity question, but synthetic variation does not by itself validate human individual differences. Precision, prior strength, environmental sampling and task construction may produce observationally similar effects; parameter recovery and model comparison must precede an interpretation of fitted parameters as psychological mechanisms.

## Source integrity issues

Two citation problems are directly visible in the archived preprint:

- P124 cites “Ding et al., 2024” for a fitted predictive-coding gratitude model, but the reference section P146–P215 contains no Ding entry. This attribution remains unresolved; no guessed replacement is entered in our bibliography.
- P122 includes “Clark, 1973” in a mood/prediction-error discussion. The actual P158 bibliography entry is *The language-as-fixed-effect fallacy: A critique of language statistics in psychological research*. Its title and domain do not identify a mood theory. We do not propagate it as support for the mood claim.

P199 and P200 also duplicate the same Sanchez and Vazquez DOI under 2014a/2014b. This does not create two independent studies. None of these issues warrants attributing fabricated work or intent to the authors; they are bounded citation-quality observations about the inspected preprint.

## Notebook boundaries and the new extension

P132 identifies the [gratitude/belief-updating notebook](https://colab.research.google.com/drive/1OaYkfpko5RO1JIKgj-Ayb_tNfdTcmt0z), archived with SHA256 `1b8a0400ba6c457d1da8ca28a369f60be2f367fb760a794c78ce7125a321ceb6`. P133 separately identifies the [modified Yarbus notebook](https://colab.research.google.com/drive/1D6KJIQgzZhpKOaX4WKgjWl10xG_ZoMdO), archived with SHA256 `ab9f36b515d1534d24b7e676841fa5cea7c264370f6ee566798c8b1b3de62510`. They are distinct source artifacts. The numerical reconstruction audit owns executable behavior and defects; this document does not infer a code failure from a narrative ambiguity or from a different tensor-axis convention.

“Thanks for Nothing” adds a new operational distinction absent from the source protocol: observed absence, missing observation, counterfactual avoided harm, and model non-reification. An absence must be represented as an actual observation under a specified detection process; missing data cannot silently become evidence of safety. Avoided harm is a contrast against a declared counterfactual, not proof that the harm would have occurred. Non-reification is our term for maintaining awareness of model alternatives or uncertainty, not a measured Buddhist attainment. These extensions must be labeled as new designs, with results separated from both faithful source reconstruction and corrected baseline experiments.

## Empirical bridge still required

A future study would need a preregistered, consented task separating gratitude, pleasant-event recall, counterfactual reflection and an expectancy-matched active comparison. It would measure gratitude, relief, indebtedness, attention and calibration separately; preserve adverse events and null outcomes; test whether parameter changes predict held-out behavior; and compare alternative mechanisms. Actual scene-transfer data would be needed to test automatic attentional change. Participant safety, construct validity and statistical power would require independent empirical design. This repository’s synthetic sample count supplies none of those guarantees.
