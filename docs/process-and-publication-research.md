# Process evaluation and publication cross-references

Targeted primary-source reading on 2026-10-19. This dossier supplies proposed prose and publication preparation recommendations. It does not certify adoption, review another worker's changes, publish a record, or establish the live state of the existing Zenodo draft. Remote access was read-only.

## Process evaluation: source and proposed integration

**Source.** Graham F. Moore, Suzanne Audrey, Mary Barker, Lyndal Bond, Chris Bonell, Wendy Hardeman, Laurence Moore, Alicia O'Cathain, Tannaze Tinati, Daniel Wight and Janis Baird. “Process evaluation of complex interventions: Medical Research Council guidance.” *BMJ* **350** (2015): h1258. Published 19 March 2015; accepted 13 January 2015. DOI [10.1136/bmj.h1258](https://doi.org/10.1136/bmj.h1258); PMID 25791983; PMCID PMC4366184. The [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4366184/) identifies CC BY 4.0. Its author-deposited full article XML was retrieved from [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4366184/fullTextXML). The BMJ full-text browser request failed; the PMC text and Europe PMC body were inspected instead.

**Precise locators.** Under “MRC process evaluation framework,” read Figure 1 and its three subsections: “Implementation: what is implemented, and how?” (paragraphs 1–3), “Mechanisms of impact: how does the delivered intervention produce change?” (paragraph 1), and “Context: how does context affect implementation and outcomes?” (paragraph 1). Also read Box 1, “Analysis.” In the retained line-separated XML these passages are at lines 309–353 and 448–472; the line-separated file is a derived aid, not the original source body.

**Proposed paragraph 1 — Methods or Discussion:** Process evaluation distinguishes implementation from mechanisms and context. Fidelity concerns delivery as intended; dose concerns the amount delivered; reach concerns whether and how the intended audience encounters the intervention. Context can alter effects even when implementation is similar [@moore2015process].

**Proposed paragraph 2 — finite-model interpretation:** Here, action frequency records activity, while alternative availability and informative access constrain what the activity can reveal. These are separate model quantities, and their relation to held-out prediction must be assessed explicitly. This use of process-evaluation distinctions is a methodological analogy: it does not validate a human intervention, establish gratitude, or measure contemplative realization.

**Claim ceiling.** Moore et al. supply evaluation distinctions, not this model's operational definitions or numerical conclusions. Their article notes disagreement over implementation subcomponents. Do not equate model support with human reach, action count with intervention fidelity, or process measurement with demonstrated benefit. The proposed second paragraph is the project's inference, grounded in the research contract, rather than an empirical claim attributed to Moore et al.

```bibtex
@article{moore2015process,
  author = {Moore, Graham F. and Audrey, Suzanne and Barker, Mary and
            Bond, Lyndal and Bonell, Chris and Hardeman, Wendy and
            Moore, Laurence and O'Cathain, Alicia and Tinati, Tannaze and
            Wight, Daniel and Baird, Janis},
  title = {Process evaluation of complex interventions: Medical Research Council guidance},
  journal = {BMJ},
  year = {2015},
  volume = {350},
  pages = {h1258},
  doi = {10.1136/bmj.h1258},
  url = {https://pmc.ncbi.nlm.nih.gov/articles/PMC4366184/}
}
```

## Verified publication mechanics

| Question | Verified behavior and exact primary locator |
| --- | --- |
| Does reservation publish a DOI? | No. Zenodo registers it when the record is published. Reservation permits inserting the identifier in files first. Deleting the draft loses the reservation. [Create new upload, “Fill in metadata,” step 2](https://help.zenodo.org/docs/deposit/create-new-upload/). |
| Can the manuscript DOI identify the code archive? | An existing DOI must identify the same object. Choose the resource type to match the actual uploaded object; mixed uploads require a deliberate choice. [Create new upload, “Fill in metadata,” steps 2–3](https://help.zenodo.org/docs/deposit/create-new-upload/). A separate software archive therefore needs its own identifier; a combined record is a different publication design. |
| What is the relation field? | The documented deposition and `.zenodo.json` field is `related_identifiers`, an array of objects containing `identifier`, `relation`, and optionally `resource_type`. `relation_identifiers` is not that field. [REST documentation, “Deposit metadata”](https://developers.zenodo.org/#representation). |
| Which relation connects software to its paper? | The official `.zenodo.json` example uses `isDocumentedBy` from software to its paper. `documents` is also in the relation vocabulary. [REST documentation, “GitHub: Add metadata to your GitHub repository release”](https://developers.zenodo.org/#github). Direction is from the record being described toward the related object. |
| Does GitHub integration require a public repository? | GitHub's instructions say Zenodo can access public repositories only. Once enabled, new releases are archived and receive DOIs. [GitHub, “Issuing a persistent identifier for your repository with Zenodo”](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content). Zenodo separately confirms automatic ingestion of new releases. [Enable a repository, introduction](https://help.zenodo.org/docs/github/enable-repository/). |
| Does restricting Zenodo files hide record metadata? | Published metadata remains public even with restricted files. [Create new upload, “Set visibility”](https://help.zenodo.org/docs/deposit/create-new-upload/). |
| Does making the existing GitHub repository public isolate a snapshot? | Visibility conversion exposes code and Actions history/logs. [GitHub, “Changing from private to public”](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility). It is not a fresh export procedure. |

The API vocabulary above is specifically the documented deposition/`.zenodo.json` representation. Do not assume its field shapes apply unchanged to a different InvenioRDM record API. Confirm the selected interface and read back its accepted representation before any later mutation.

## Proposed object and link plan

These are recommendations, conditional on the author's selected record type and authorized release contents; they are not a claim that this publication plan has been executed.

1. Identify the object represented by the existing reserved manuscript DOI. [THIRD_PARTY.md](../THIRD_PARTY.md) records `10.5281/zenodo.23402517` as a manuscript reservation. This assignment did not independently inspect the authenticated draft; that local statement is not fresh proof of its status. Preserve its manuscript role unless the author explicitly chooses another record design.
2. If publishing separate manuscript and software records, use the software record's own version DOI in code citation metadata and the release README. Describe the manuscript as documentation with software → manuscript `isDocumentedBy`; use manuscript → software `documents` if that accurately describes the relationship. An archive-to-GitHub `isSupplementTo` or `isIdenticalTo` relation must be chosen according to actual contents; identity requires matching objects, not merely related projects. These relation selections are project recommendations using the [documented vocabulary](https://developers.zenodo.org/#representation).
3. Link the GitHub README and release notes to the software DOI and separately label the manuscript DOI. In the Zenodo description include the exact GitHub release URL and commit permalink. Keep reserved identifiers visibly marked as reserved until publication and verify both landing pages afterward. For a combined manuscript/software record, describe the combined object and link GitHub to it without inventing a second DOI.
4. Resolve mutual links before the proposed single snapshot commit: reserve only the authorized object identifiers, insert final metadata and release URLs, then freeze the allowlisted files. A release tag and later Zenodo metadata edits need not add another Git commit. Do not enable automatic GitHub archiving while also planning an unrelated manual record for the same object without deciding which workflow owns the software DOI.

## Fresh snapshot while preserving private history

Recommended preparation: retain this private repository and its history; copy only reviewed, explicitly allowlisted release files to a separate GitVault directory without `.git`, credentials, caches, private research receipts, or excluded source artifacts. Initialize that directory independently and make the one intended snapshot commit there. Git's [git-init documentation, “Description”](https://git-scm.com/docs/git-init) states that a new repository starts with an initial branch without commits. Reinitializing the existing checkout preserves its existing repository; it does not clear history.

Before publishing the prepared repository, verify its file manifest, every included third-party asset's recorded terms, one reachable root commit, no additional refs carrying private history, reproducibility from the exported files, and the intended destination. These are future acceptance checks, not performed checks in this research assignment. Do not use a mirror push or convert the current private repository merely to satisfy the one-snapshot requirement.

The current [THIRD_PARTY.md](../THIRD_PARTY.md) explicitly separates original-code MIT licensing from source receipts and dependencies. It records no independent notebook software license and limits the retained Realizing Emptiness paper to private provenance. Their local presence does not supply a new redistribution license. A public export should omit such files unless their inclusion has a separately established basis; preserve the private originals. GNN's separately declared CC-BY-NC-SA-4.0 terms and the Munch photograph's attribution also remain distinct. This is an inventory boundary, not a new legal conclusion or license grant.

## Retrieval and evidence

Raw bodies, retrieval times, final URLs, HTTP status, content types, byte counts and SHA256 values are retained under the mounted GitVault volume at `Local/tmp/tfn-final-polish-20261019/research/`. `retrieval.json` binds seven successful HTTP 200 responses to their downloaded bytes. The Moore XML SHA256 is `8be1f3ef92610d36fa54549306324a5eee660360183fbd8f2abfe9b5542cce38` (61,302 bytes). `moore2015-lines.xml` adds line breaks between tags for reproducible passage locators. No complete article body is added to the repository.

| Scenario | Invocation | Binary observable | Captured artifact |
| --- | --- | --- | --- |
| Retrieve primary bodies | Node `fetch(url)` and `writeFile`, exact URL list in receipt | All seven statuses equal 200 and bodies are nonempty | External `retrieval.json` and seven named source files |
| Verify source identity and relevant passages | `node verify-research.mjs` in the external research directory | Expected DOI, implementation terms and official field/status statements present; every receipt hash matches | `.omo/evidence/process-publication-20261019.json` |
| Challenge the source check | Same invocation, intentionally nonexistent title marker | Real identity accepted and false identity rejected | Same evidence JSON, `negative_control` |
| Verify the deliverable | Same invocation | Dossier is nonempty and contains the proposed prose, BibTeX and publication links | Same evidence JSON, `dossier` |

These checks establish retrieval integrity and targeted document coverage. They do not validate the scientific model, demonstrate publication, certify licensing, or independently approve the manuscript.
