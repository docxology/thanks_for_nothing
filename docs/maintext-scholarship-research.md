# Main-text scholarship check

Historical note: targeted reading completed on 2026-10-19 for expansion of the main Methods, Results and Discussion. These are proposed integrations, not a claim that the manuscript already contains them. The assignment introduced no bibliography entries, numerical results, quotations, catalog upgrades or human experiments.

The reading scope was the current `docs/manuscript/manuscript.md`, the supplement's conceptual distinctions, estimand and empirical-design passages, and the five existing sources below. Earlier dossiers supplied retrieval pointers only. Their summaries and receipts were not treated as independent confirmation of the papers' claims.

## Access and provenance

Fresh primary bodies were retrieved and the identified passages inspected for **all five sources** below. The browser tool returned challenges for PMC and eLife and an access failure for Europe PMC; these failed probes were not counted as readings. Direct retrieval subsequently returned readable PMC HTML for Choi and Dahl, Europe PMC full-text XML for Wilson and Morris, and publisher HTML for Fleming and Lau. Fleming and Lau was also read through the publisher's browser-accessible full text.

Raw bodies, readable extracts and URL/status/digest records are retained under `.omo/evidence/maintext-scholarship-20261019/`. `retrieval.json` identifies the fresh bodies; `verification.json` checks their identity and the deliverable. The new files are task evidence, not additions to the source catalog. A response status alone was insufficient: article identity and relevant passages were read in the captured body.

Existing local originals were located at `data/scholarship/receipts/revision/morris2019-fulltext.xml`, `receipts/v040/wilson2019.xml`, `receipts/v040/dahl2015-pmc.html` and `receipts/v070/fleming2014.xml` beneath the same scholarship directory. The existing Choi receipt points to its earlier retained HTML outside the checkout. Fresh checks below supersede reliance on those receipts for these particular passages; they do not upgrade access elsewhere in the catalog. Other cited works, including the Fisher journal publication, retain their earlier access ceilings and were not newly verified here. No supplementary dataset, meta-analysis code or human raw data was reanalyzed.

## Proposed main-text integrations

### Comparator content limits the interpretation of recall

**Existing key:** `gratitudemeta2025`. **Primary source:** [Choi and colleagues](https://pmc.ncbi.nlm.nih.gov/articles/PMC12280877/). **Inspected:** Results, Moderator Analyses: Separate Models; Table 2, control-type rows; Discussion, country-proxy and English-language limitations; Materials and Methods, Effect size and variance calculations. Artifact: `choi.txt`.

**Suggested placement:** Discussion, after the distinction between agreeable evidence and appreciation of inquiry; cross-reference the recall result.

**Proposed paraphrase:** A recent synthesis reports aggregate well-being gains while finding no statistically significant advantage over positively valenced activities. That comparison does not establish equivalence. Country served as a cultural proxy, and the search included English-language studies, limiting cultural generalization. Our dose-matched replay comparison isolates a computational selection rule; it cannot establish that gratitude-specific meaning explains human outcomes [@gratitudemeta2025].

**Ceiling:** Preserve the unresolved discrepancy: the adjacent prose denies a control-type omnibus moderator, whereas Table 2 presents an omnibus result pointing differently under an unadjusted reading. The methods mention multiplicity adjustment; this check did not resolve the discrepancy. Import no omnibus conclusion. Neither comparator nonsignificance nor aggregate benefit identifies the implemented precision mechanism or validates an absence-based intervention.

### Confidence, monitoring and task performance require separate observations

**Existing key:** `fleminglau2014`. **Primary source:** [Fleming and Lau](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2014.00443/full). **Inspected:** Introduction and Figure 1; Measures of metacognitive sensitivity; Type 2 ROC analysis; Model-based approaches. Artifact: `fleming.txt`.

**Suggested placement:** Expand Discussion, From where one looks to what one understands, then connect to the scene/encoding results.

**Proposed paraphrase:** Higher reported confidence need not improve discrimination between correct and incorrect decisions. Metacognitive sensitivity concerns that discrimination, whereas efficiency evaluates sensitivity relative to first-order task performance. A human translation must therefore collect confidence and correctness together and account for task performance, rather than treating lower uncertainty or altered gaze as sufficient evidence of improved monitoring [@fleminglau2014].

**Ceiling:** This is a measurement framework, not evidence that the proposed practice improves metacognition. The model's entropy and encoding Brier score do not become human sensitivity or efficiency measures by relabeling them. No human confidence model or meta-d-prime estimate was fitted here.

### Exact replay does not establish psychological identification

**Existing key:** `wilson2019`. **Primary source:** [Wilson and Collins](https://doi.org/10.7554/eLife.49547), read through [Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6879303/fullTextXML). **Inspected:** `s7` and `s7-1`/`s7-4`, parameter recovery; `s8` and `s8-2`/`s8-4`, model recovery and candidate-set limits; `s10`, generative validation. Artifact: `wilson.txt`.

**Suggested placement:** Discussion, Identification, limits and a testable empirical program; connect to label-equivalent and excluded-encoding results.

**Proposed paraphrase:** Human parameter interpretation requires recovery over the relevant parameter range, recovery of competing models, and reproduction of behavioral patterns beyond relative fit. A model can win because its rivals are worse while remaining inadequate. Exact software replay and finite evidence calculations answer different questions: they verify specified computation without identifying a psychological mechanism or demonstrating that the candidate menu is sufficient [@wilson2019].

**Ceiling:** The tutorial supports these validation requirements; it does not certify this implementation. The project's observational-equivalence and support restrictions are its own formal results. They are not human recovery experiments, and increasing synthetic replication cannot substitute for a discriminating experimental design.

### State the target before interpreting uncertainty

**Existing key:** `morris2019`. **Primary source:** [Morris, White and Crowther](https://doi.org/10.1002/sim.8086), read through [Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6492164/fullTextXML). **Inspected:** Estimands and other targets (`sim8086-sec-0006`); Methods (`0007`); performance and Monte Carlo uncertainty (`0016`); simulation sample size (`0017`); Remarks on analysis (`0018`). Artifact: `morris.txt`.

**Suggested placement:** Methods, Estimands, uncertainty and reproducibility; recall Results interpretation.

**Proposed paraphrase:** Following the separation of generating mechanisms, targets and performance measures, our fixed-world average is a declared target rather than a population estimate for people. Reweighting worlds changes that target. Within each independent simulated unit, policy outcomes remain paired; repeated decisions do not create independent replications. More simulated units improve precision for the declared process, while known-answer checks separately assess interval behavior [@morris2019].

**Ceiling:** Fixed-world weighting and the paired-unit rule are applications to this project's design, not verbatim prescriptions from the tutorial. The source distinguishes targets and Monte Carlo error; it does not validate the project's bootstrap, establish coverage everywhere, or supply human-trial power. Retain unavailable estimates and known-answer failures rather than treating precision as proof of adequacy.

### Specify what practice is intended to change

**Existing key:** `dahl2015`. **Primary source:** [Dahl, Lutz and Davidson](https://pmc.ncbi.nlm.nih.gov/articles/PMC4595910/). **Inspected:** The Constructive Family: Reappraisal, Perspective Taking, and Self-Schema; Deconstructive Family: Self-inquiry and Insight; Concluding Remarks and Future Directions. Artifact: `dahl.txt`.

**Suggested placement:** Discussion, Gratitude for the practice of realizing emptiness, immediately before the empirical proposal.

**Proposed paraphrase:** A proposed taxonomy distinguishes attentional practices, constructive changes in interpretation and affect, and deconstructive inquiry into experience. Meta-awareness can prepare inquiry while remaining a different process. This motivates specifying whether appreciation is intended to support engagement, recognition of an assumption, or its examination, and measuring these links separately within their ethical, interpersonal and cultural setting [@dahl2015].

**Ceiling:** The taxonomy is a framework with acknowledged empirical gaps. The proposed appreciation-to-inquiry connection is our synthesis, not an established causal result of the source. Its historical account of research gaps is not a claim about the complete current literature. Finite family switching does not establish contemplative realization or clinical benefit.

## Integration and verification record

Promote the reasoning already developed in the supplement rather than adding an independent literature survey. Methods should explain the inferential target and unit; Results should state what changes across controls and contexts; Discussion should connect those patterns to identifiable future measurements. Retain all adverse findings and avoid adding numerical human comparisons to the simulation results.

Verification used the environment bindings supplied for this review. The external volume was mounted, and the invoked Python environment and base interpreter both resolved on GitVault. `omo-agent-toolkit ulw-loop status --json` reported no active plan, so artifacts use `.omo/evidence/`.

| Scenario | Invocation | Binary observable | Captured artifact |
| --- | --- | --- | --- |
| Primary access and article identity | Direct `urllib.request.urlopen` of the URLs recorded in the retrieval manifest; XML/HTML body inspection | All required article bodies retrieved; source-specific DOI and inspected-section markers present | `.omo/evidence/maintext-scholarship-20261019/retrieval.json`, source `.body` and `.txt` files, `verification.json` |
| Existing citation keys and bounded deliverable | `uv run python .omo/evidence/maintext-scholarship-20261019/verify.py` | Every proposed key exists in catalog and bibliography; every recommendation has a source, locator, paraphrase and ceiling | `.omo/evidence/maintext-scholarship-20261019/verification.json` |
| Identity gate can reject a wrong source | Same verification invocation with an intentionally incorrect DOI passed internally | Wrong identity rejected; real identities accepted | `.omo/evidence/maintext-scholarship-20261019/verification.json` |

These checks establish provenance and document structure. Scholarly adequacy rests on the targeted reading recorded above; the checks are not an independent review of the interpretation or a rerun of numerical experiments.
