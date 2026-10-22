# Realizing Emptiness integration research

Research date: 2026-10-15. This report supports the requested extension of *Thanks for Nothing* from appreciating an avoided harm to preferring and practicing an examinable relationship to one's models. Its recommendations are new finite modeling proposals. The numerical checks below establish API conformance and bounded upstream diagnostics; they do not establish human realization, practice efficacy, compassion, or philosophical truth.

## Source identity and access

The inspected Realizing Emptiness source is commit `bd91fa1c230551180ed741d1951840e3628da35d`, version 3.0.0. Its local checkout was clean at the initial inspection. The public [repository](https://github.com/docxology/realizing_emptiness) was accessed read-only; the browser could not fetch the commit-tree URL, so exact source citations below were verified against local Git blobs. Seven installed modules and eight admitted GNN declarations were checked byte-for-byte or by SHA-256 against that commit before the numerical probes. This is stronger than relying on a version string. The report does not assign the repository's older archive DOI to version 3.0.0.

| Primary source | Access actually obtained | Permitted role |
| --- | --- | --- |
| Sandved-Smith, Fields, Doctor, Laukkonen and Hohwy, *There is no self-evidence: A physics of emptiness realisation*, 23 May 2026 | Full local 25-page PDF available; targeted reading of sections 4.1–4.3, 5.1–5.3 and 6.1–6.2, especially printed pp. 12–20. The [OSF version-one landing page](https://osf.io/preprints/psyarxiv/m78z2_v1) returned 403 during this pass. | Source of the conceptual proposal and its stated mathematical argument; not an empirical intervention study. |
| Realizing Emptiness implementation and declarations | Exact pinned source inspected; installed APIs exercised as detailed below. | Finite operational comparators and specification admission. |
| [SN 12.15, Thanissaro Bhikkhu translation](https://www.dhammatalks.org/suttas/SN/SN12_15.html) | Full translated discourse and translator notes accessed. | Interpretive constraint: the discourse rejects the existence/nonexistence extremes and explains conditioned origination and cessation. It does not specify Bayesian inference. |
| [MN 121, Thanissaro Bhikkhu translation](https://www.dhammatalks.org/suttas/MN/MN121.html) | Full translation accessible; inspected the opening absence/presence distinction, “Nothingness,” “Theme-less Concentration,” and “Release.” | Interpretive constraint: attention to absence retains what remains; even refined concentration is considered conditioned. A state labeled nothingness is insufficient to identify realization. |

The source PDF remains at `docs/There_is_no_self_evidence_Sandved-Smith_2026.pdf` within the Realizing Emptiness checkout, with verified SHA-256 `94e2335c3a4a37b8d49039b11b45ccda25bad65d4b80aa15428b84abfba699ac`. The authoritative relative location and provenance are in the [pinned source manifest][manifest]. No downloaded paper was modified. This research adds no claims based on unread secondary books or abstracts.

## The precise manuscript gap

The baseline inspected here is TFN commit `f641df0a1b912cb4179d1ed2814fbc61212f1fc9`. Its manuscript already distinguishes observed absence, missing evidence, counterfactual value, and label-invariant representation. “Emptiness, residual presence and representation” restricts non-reification to a modest modeling discipline; “Absence, counterfactual value, and information controls” tests consistent label permutation. The corresponding [`nothingness.py`, lines 72–105][tfn-nothingness] changes label order but neither chooses inquiry nor revises an inference architecture. The [model contract][tfn-contract] states that the passive study's zero preference vector has no policy role.

Consequently the manuscript cannot yet support a computational account of *preferring the practice of realization*. An avoided-harm valuation is a counterfactual appraisal. Label invariance is a consistency property. Neither, by itself, is the selection and repeated enactment of an activity that makes an assumption examinable. The proposed extension should add that distinct question while preserving the existing semantic controls.

Recommended thesis: **An agent can value the opportunity to examine how its models depend on conditions, select activities that expose otherwise fixed assumptions, and retain or revise those assumptions according to their predictive contribution.** This is the report's synthesis, not a quotation or a demonstrated human mechanism. Its finite implementation must separate preference, chosen activity, access to alternatives, evidence evaluation, and ensuing revision.

## What the source argument actually licenses

1. **Opacification is access to a previously implicit assumption.** Section 4.2, pp. 13–14, proposes that tracking changes in attention and framing makes an otherwise transparent separation constraint available for examination. A useful finite counterpart makes the identity or parameters of a model selectable or inferable. Merely lowering its precision on a schedule is a declared intervention on access, not a learned metacognitive achievement. The upstream [practice vocabulary][practice] names attentional opacification and dependent-origination inquiry, but its [GNN declaration][practice-gnn] explicitly says the deltas are metadata never applied to simulation.

2. **Dependent-origination inquiry concerns conditions of construction.** Section 4.2, p. 14, connects examining framing and sectorization to conditioned arising. A finite task can compare an action-conditioned channel with an action-independent channel, or ask when a partition remains useful after a context change. This operationalization samples a narrow computational question; it does not encode the complete dependent-origination doctrine. The named SN 12.15 translation supplies an interpretive boundary rather than an algorithm.

3. **The source removes compulsory commitment, not useful modeling ability.** Section 4.1, pp. 12–13, gives action prediction, planning and coordination as reasons factorization can help. Section 5.2, p. 17, retains boundary designations as pragmatically useful options. Therefore a successful TFN extension must sometimes preserve structured models. Treating every reduction, every lower precision, or every larger entropy as progress contradicts this part of the proposal.

4. **The BMR argument is conditional.** Section 4.3, pp. 15–16, equations (11)–(12), compares complexity and accuracy after a flexible metacognitive model already sustains the relevant predictions. Footnote 7, p. 15, explicitly excludes the cost of acquiring that metacognitive capacity from this particular comparison. TFN should therefore distinguish the conditional benefit of removing a redundant commitment from the total cost of obtaining and using access. Neither the preprint argument nor a favorable toy comparison establishes that arbitrary reductions improve evidence.

5. **Revision must remain responsive after the first reduction.** Section 5.3, p. 18, treats designations as maintainable, revisable or discardable as conditions change. Section 6.1, p. 19, distinguishes enacted context sensitivity from a proposition about contextuality. A test that repeats a statement of non-reification without changing model selection should show no mechanistic benefit. “I am no longer attached” is not a measurable transition in the finite model.

6. **Practical scope needs an explicit objective.** Section 6.2, pp. 19–20, argues that lifting a restriction and orienting engagement are connected but distinguishable. The software's scope-of-concern quantity weights action influence and a stipulated self-sector precision boost. It measures neither compassion nor welfare. Any TFN policy that values broader scope inherits a normative modeling choice requiring disclosure and ablation, not a moral conclusion inferred from BMR.

All six points paraphrase the [hash-bound source PDF][paper], at the locators given. The preprint's stronger phenomenological, physical and philosophical interpretations should be attributed as proposals rather than adopted as results of TFN.

## Executable interfaces and their limits

| Available interface | Exact authority | Appropriate use and limitation |
| --- | --- | --- |
| `practice.protocols.practice_protocol_map()` | [Implementation, lines 9–40][practice]; [practice GNN, lines 10–21][practice-gnn] | Three declared practice-to-parameter mappings and `allow_user_facing_claims=False`. These provide vocabulary/provenance; they do not enact practice or update a simulation. |
| `simulation.bmr.compare_models(prior_precision, metacognitive_access)` | [Implementation, lines 18–33][bmr]; [finite BMR declaration, line 23][bmr-gnn] | A stipulated linear accuracy/complexity sweep. Access affects the accuracy bonus and reduced complexity by construction. Useful for sensitivity/comparison, insufficient as the core claim that inquiry learned to remove an unsupported model. |
| `formalism.models.FreeEnergyTerms.from_distributions(...)` and `BMRComparison(...)` | [Implementation, lines 189–273][vfe] | Genuine finite categorical KL and expected log likelihood. Supplies a transparent evaluator for new declared candidates. `delta_free_energy` is reduced minus full, and pruning requires a strictly negative result. The caller supplies the candidate distributions, data model, and any noise term. |
| `simulation.emergence.build_ongoing_revision_audit(*, steps=None, seed=None, channels=None)` | [Implementation, lines 122–227][revision]; [finite emergence declaration, line 23][revision-gnn] | Changes which binary channels depend on actions, compares rigid and revised partitions, and includes a stationary-stream control. It selects and scores each partition on the same window at lines 169–173. It is an in-sample finite diagnostic, not held-out predictive validation or online changepoint inference. |
| `simulation.compassion_scope.compute_scope_of_concern(...)` and `build_compassion_scope_audit(deployments, ...)` | [Concern calculation, lines 132–197][scope]; [audit controls, lines 204–279][scope-controls]; [scope declaration, line 23][scope-gnn] | Combines realized action influence with imposed precision weights; compares per-channel means rather than raw partition sums. Existing controls ablate self-precision and disrupt action/observation pairing. Its output is policy-scope arithmetic, not affective compassion. |
| `modeling.registry.parse_model`, `load_model`, `model_parameters` | [Admission and loading, lines 103–180][registry]; [GNN authority guide, lines 10–55][gnn-guide] | Real upstream parser and strict semantic validation bind a source hash to tensors or finite parameters. Model-specific constraints still need validation: general finite admission does not establish an arbitrary utility's scientific meaning. |

TFN's baseline [loader, lines 39–60][tfn-loader] always validates categorical A/B/C/D tensors. A new `FiniteSurrogate` declaration should use an explicit finite adapter or extend admission deliberately; passing it through the existing categorical adapter is not supported merely because the upstream registry accepts it. Keep arbitrary preference weights, costs, access schedules, context schedules and candidate definitions in GNN, with typed domain checks and source hashes in outputs.

### A defensible mathematical core

For each candidate model, use the source's finite VFE decomposition:

\[
F_m(q,o)=D_{\mathrm{KL}}(q\Vert p_m)-\sum_s q(s)\log L_m(o\mid s),\qquad
\Delta F=F_{\mathrm{reduced}}-F_{\mathrm{full}}.
\]

With an exact posterior, independently verify `F == -log(sum(prior * likelihood))` in a small enumerated example. This checks the evaluator against marginal likelihood; it does not show a state factor has become philosophically unreal. A smaller state space alone does not guarantee smaller KL, and two models must use the same observations and consistent evidence conventions. Forcing a desired posterior or adding an arbitrary positive “rigidity cost” changes the construction and must be reported as such.

The API's default KL unit is bits, but it does not convert the supplied log-likelihood array. Use `base=np.e` with `np.log`, or `base=2` with `np.log2`, consistently. Do not silently combine bits and nats. Validate finite likelihood inputs and the support of probabilities before calling the evaluator; the public function checks likelihood shape but is not a complete scientific-model validator. These requirements follow directly from [lines 198–220][vfe] and [the KL calculation][kl].

Treat policy choice as a separate proposed layer. For example, select an inquiry policy using a declared utility containing anticipated predictive value, an explicit preference for examinability, and an activity cost. If a finite softmax is used, expose its temperature and all terms. An examinability preference must not insert favorable observations, guarantee a reduced model's victory, or reward an attainment label. Record both expected utility and realized independent performance; an increase in the utility that the programmer designed the policy to maximize is not independent evidence of benefit.

Access can gate whether candidates are available. However, a rule such as `access += declared_step` after each chosen activity is a scheduled mechanism, not learned access. A more demanding future version could learn the reliability of frames or intervention outcomes from observations. The current sources do not supply that learned practice engine. Root implementation may enact new GNN-declared interventions, but should explicitly call them new TFN constructions.

## Discriminating experiment design

Use paired exogenous streams and separately seeded training and assessment data. Freeze candidate selection before evaluating the held-out context. If the environment changes, identify whether the experiment gives the agent the change time or requires detecting it; the upstream windowed audit assumes the former segmentation.

| Contrast | Observable that can discriminate the explanation | Failure interpretation |
| --- | --- | --- |
| Useful structure versus redundant commitment | A candidate with an indispensable accuracy advantage is retained; removing a redundant restriction can win only when its accuracy loss is sufficiently small. Report both terms of delta F. | Always preferring the smallest model demonstrates a programmed reduction bias. |
| Stationary versus changing context | Revision advantage is concentrated after actual change, with independent predictive loss reported for both streams. | A stationary advantage may reflect selection flexibility, noise fitting or a separate benefit; it is not evidence specific to adaptation. |
| Inquiry versus dose-matched sham | Same activity count and computational budget, but sham exposes no new structural alternative or informative intervention. Record action, access and candidate traces. | Equal effects undermine the proposed access mechanism; different costs or observations would confound the comparison. |
| Preference versus zero added preference | Remove only the preference for inquiry while holding its cost, evidence and available options fixed. Track policy probabilities and chosen activities separately from inference. | A no-preference agent can still inquire for predictive reasons. Zero added preference does not logically require zero inquiry. |
| Access versus no access | The preference can remain high while access to candidate revision is blocked. | Valuing inquiry without revision distinguishes aspiration/selection from enacted structural change. |
| Evidence mismatch | Supply data favoring the allegedly rigid candidate; the evidence evaluator must permit retention despite the practice preference. | Preference overriding contradictory evidence is motivated model selection, not improved calibration. |
| Repeated claims versus actual revision | Repeat a descriptive label without changing distributions, action choice or candidate access. Model evidence and predictions should remain unchanged. | Improvement caused by a label alone reveals a bookkeeping or interpretation error. |
| Scope precision versus action influence | Hold labels/partition size fixed, ablate the self-precision boost, then shuffle action/observation pairing. | A widening score can otherwise be a relabeling or imposed-weight artifact. |
| Fresh evidence versus rehearsal | Preserve event identities, replay dose and source exposure hashes. | Repeated reflection must not count as independent sensory confirmation. |

These are proposed TFN acceptance scenarios, not claims that the new experiment has already passed. Prefer thresholds tied to numerical accuracy, independent scoring and declared contrasts over a gate that demands psychological improvement. Retain unfavorable results and separate a failed hypothesis from failed software.

## Concrete manuscript integration

1. **Introduction and abstract:** add the positive research question of preferring and enacting inquiry into model commitments. Preserve the separate avoided-harm question. Define the extension as finite policy selection and revisability, so “practice” names an explicit activity and “realization” remains the motivating source concept.
2. **Scholarship:** expand the present “Emptiness, residual presence and representation” section with the source sequence: implicit separation assumption, opacification, conditional model comparison, retained pragmatic structures, continuing revision. Cite printed pp. 13–18. Attribute the source's interpretive claims rather than identifying them with established Buddhist consensus.
3. **Methods:** introduce separate numbered equations for candidate VFE, the model-comparison sign convention, policy preference/cost, and any access transition. State which equations are imported evaluators and which are new TFN assumptions. Do not call an externally imposed access schedule an inferred skill. Account for the acquisition cost omitted from the source's conditional BMR comparison.
4. **Results:** report behavior only after actual execution: chosen inquiry rate, available candidates, reduced/full evidence differences, retained useful structures, and held-out predictive loss by context. Include no-preference, no-access, sham and evidence-mismatch rows even when the intended effect fails. Keep the upstream in-sample audit in an interoperability subsection.
5. **Discussion:** explain the distinction between valuing inquiry, obtaining access, revising a model, and contemplative attainment. A finite agent may rationally preserve a useful distinction. Avoid making a lower free-energy number an index of wisdom or a larger concern share an index of compassion.
6. **Practical implications:** propose an empirical design that measures choice to engage, task performance and belief revision separately, alongside independently validated contemplative/affective measures. The software practice map alone supports no user-facing efficacy guidance.

Suggested replacement framing for the present non-reification discussion: “The extension treats model descriptions as revisable instruments. A declared preference can motivate inquiry into the conditions under which a description is useful; inquiry can make alternative descriptions available; evidence can then favor retaining or revising the current description. These are distinct operations. Their finite realization supplies a testable modeling proposal without identifying the modeled transitions with human realization of emptiness.” This paragraph is proposed manuscript prose, not a result statement.

## Verification performed for this report

The invocation below ran from the TFN checkout using the existing external Python 3.14 environment. Its `sys.prefix` and `sys.base_prefix` were verified on GitVault. No environment synchronization, sibling pipeline, publication or DOI operation was performed.

```sh
env UV_PROJECT_ENVIRONMENT=/Volumes/GitVault/Local/evidence/thanks-for-nothing-20261015/venv \
  UV_CACHE_DIR=/Volumes/GitVault/Local/evidence/thanks-for-nothing-20261015/uv-cache \
  UV_LINK_MODE=copy \
  TMPDIR=/Volumes/GitVault/Local/evidence/thanks-for-nothing-emptiness-revision-20261015/research \
  MPLCONFIGDIR=/Volumes/GitVault/Local/evidence/thanks-for-nothing-emptiness-revision-20261015/research \
  PYTHONDONTWRITEBYTECODE=1 \
  uv run --no-sync python .omo/evidence/emptiness-integration-research/probe.py
```

| Scenario | Binary observable | Captured artifact |
| --- | --- | --- |
| Source and runtime identity | Seven installed module files and eight admitted GNN hashes match pinned Git blobs; source PDF hash matches; both Python prefixes external | `.omo/evidence/emptiness-integration-research/probe-result.json`, `identity` |
| Categorical VFE conformance | Exact-posterior VFE equals negative log evidence to `1e-12`; contradicted prior loses, supported prior wins, identical models do not prune | Same artifact, `categorical_vfe_prior_mismatch`, `categorical_vfe_supported_prior`, `tie`; assertions in `probe.py` |
| Invalid posterior control | Posterior `[0.8, 0.8]` raises `ValueError` with “posterior and prior must each sum to 1” | Same artifact, `invalid_posterior` |
| Practice mapping | Three expected protocol IDs and `allow_user_facing_claims == false` | Same artifact, `practice` |
| Ongoing revision | Default audit controls true and exact replay equals the first run | Same artifact, `ongoing_revision`; replay assertion in `probe.py` |
| Scope audit | Default upstream scope audit's controls true, including its ablations | Same artifact, `compassion_scope` |

These are freshly executed observations. The VFE fixtures compare priors over a fixed state space; they do not themselves implement removal of a state factor or a learned practice trajectory. The upstream audits retain their in-sample and stipulated-weight limits. The captured `probe.log` records the successful process output. The recommended TFN experiment and root's subsequent implementation were not independently reviewed by this research worker.

[manifest]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/data/sources/source_manifest.yaml#L1-L17
[paper]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/docs/There_is_no_self_evidence_Sandved-Smith_2026.pdf
[practice]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/practice/protocols.py#L9-L40
[practice-gnn]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/modeling/specifications/practice_mapping.gnn.md#L10-L21
[bmr]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/simulation/bmr.py#L18-L33
[bmr-gnn]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/modeling/specifications/finite_bmr.gnn.md#L22-L23
[vfe]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/formalism/models.py#L189-L273
[kl]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/formalism/models.py#L128-L151
[revision]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/simulation/emergence.py#L122-L227
[revision-gnn]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/modeling/specifications/finite_emergence.gnn.md#L22-L23
[scope]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/simulation/compassion_scope.py#L132-L197
[scope-controls]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/simulation/compassion_scope.py#L204-L279
[scope-gnn]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/modeling/specifications/finite_compassion_scope.gnn.md#L22-L23
[registry]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/src/modeling/registry.py#L103-L180
[gnn-guide]: https://github.com/docxology/realizing_emptiness/blob/bd91fa1c230551180ed741d1951840e3628da35d/docs/gnn-modeling.md#L10-L55
[tfn-nothingness]: https://github.com/docxology/thanks_for_nothing/blob/f641df0a1b912cb4179d1ed2814fbc61212f1fc9/src/thanks_for_nothing/nothingness.py#L72-L105
[tfn-loader]: https://github.com/docxology/thanks_for_nothing/blob/f641df0a1b912cb4179d1ed2814fbc61212f1fc9/src/thanks_for_nothing/specifications.py#L39-L60
[tfn-contract]: https://github.com/docxology/thanks_for_nothing/blob/f641df0a1b912cb4179d1ed2814fbc61212f1fc9/docs/model-contract.md
