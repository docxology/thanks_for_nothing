# Manuscript production

The [main IMRAD text](manuscript/manuscript.md),
[technical supplement](manuscript/supplement.md) and
[caption catalog](manuscript/captions.yaml) are the authoring components.
The pipeline produces a composed Markdown source, PDF, standalone HTML, numbered
equation/figure registries, the variable ledger, renderer logs and artifact inventory.

It also builds the [traditions atlas companion](../output/world_traditions.html)
from [authored textual rows](../data/scholarship/traditions.json) resolved against
the scholarship catalog. The same admitted record generates the manuscript
figure. Content, edition locators and interpretation live in data; shared
typography and layout stay in rendering code. The companion is local and
self-contained, with source links, searchable details and explicit limits.

## Composition and numerical authority

[The value contract](manuscript-values.md) defines producer-bound quantities,
caption expansion, literal admission and deterministic composition replay.
Every changing experimental value uses a producer token. Complete model settings,
statistical comparisons, adverse findings and unavailable estimates remain in the
supplement. Main Results retain the task/readout composites; detailed comparison
charts do not displace the cognitive setting.

Current version, figures, equations, scholarship count and layout values are
[generated from the run](../output/reports/research_summary.md). Maintained guides
do not supply another set of protocol defaults.

## Main text and supplemental evidence

The [reading guide](manuscript-reading-guide.md) maps research questions to their
main explanations and exact supplemental evidence. Each Results subsection
should explain the comparator, what changed, what the result establishes and
which alternative explanation remains. The main text must contain enough
reasoning to stand on its own; a supplemental link provides the derivation,
complete comparison or diagnostic rather than replacing that explanation.

Prefer a claim-specific link to a stable section, figure or equation identifier.
For example, link a weighting qualification to the weighting display and a
parameter-confounding claim to its derivation. Use separate links when an exact
count result and a repeated-policy result have different scopes. Do not describe
a link to an entire Results section as if it targeted a particular interval
table. Keep the existing identifiers when editing nearby prose.

Writing changes still require a new composed artifact and source receipt.
Check source-fragment closure, rendered HTML targets, resolved figure/equation
references and citations, then inspect the new PDF page breaks. A working link
proves that a target exists, not that it supports the associated sentence.
The [targeted main-text dossier](maintext-scholarship-research.md) records the
primary readings behind the expanded explanations and their interpretation limits.

## Cover, identity and DOI status

The cover is followed by two full-page graphical abstracts, a dedicated GNN model
card on physical page four, then the contents on page five.
The cover's framing, repository link and revision date come from metadata in
both PDF and HTML. The conceptual abstract reuses the defined symbolic
operations from the main concept figure. Its colors follow the same semantic
registry; diagrams describe operations rather than observed effects. Each PDF
abstract includes concise links to its supporting manuscript sections.
[The declarative abstract catalog](manuscript/graphical-abstracts.yaml) supplies
conceptual operations, experimental comparisons, findings and limits. Scientific
quantities resolve from the same admitted scalar ledger as the main text;
unresolved quantities and missing target sections fail rendering. These images
are front matter, separate from numbered scientific figures. PNG, SVG and vector
PDF exports retain configuration, scalar-ledger and image digests in
`reports/graphical_abstracts.json`. HTML includes full descriptions and links to
the detailed evidence. PDF pages use the vector originals.

The experimental abstract shows six distinct comparisons, including absence,
native attention/transfer and both scene-inquiry tasks. Its conditional-model
glyphs and dimensions derive from the executed GNN catalog. It shows a selected
recall-world stratum while the complete cards expose every stratum and regime.
The abstract receipt binds the graph catalog as well as authored prose and the
scientific scalar ledger; stale graph dimensions fail admission.

`render_manuscript(..., graphical_abstracts=False)` explicitly supports isolated
renderer fixtures without a composed research ledger. Normal production follows
the `graphical-abstracts` metadata setting and requires the ledger. Publication
validation requires both abstracts, the model card and their cover–abstracts–model-card–contents–manuscript
reading order.

The [model-card renderer](../src/thanks_for_nothing/gnn_model_card.py) derives its
inventory from admitted GNN arrays and source-bound numerical consumers. The
Bayesian time slice is a mathematical POMDP definition conditional on actions;
the separate parsed declaration graph may contain cycles. These are distinct
representations. All scientific dimensions and execution labels are injected.
The complete `frontmatter/gnn-model-card.html` and `.json` companions retain every
declaration, tensor, parameter, annotation, native asset and consumer digest,
plus installed dependency versions and available revision receipts. The PDF
page links to methods, model inventory, limits and the relative complete-card
companion; HTML also links directly to the cards. `reports/gnn_model_card.json` binds the generator, catalog,
consumer metadata and exported bytes. Validation rejects repaired-hash catalog
role forgeries and stale or missing companions.

[Metadata](manuscript/metadata.yaml) supplies title, subtitle, author, affiliation,
email, ORCID, version, date, DOI status, cover description and PDF layout.
ORCID admission checks the ISO check digit. Cover bytes are admitted against
[conceptual-art provenance](manuscript/assets/cover-provenance.json); the image
is artwork, separate from the scientific figure inventory.

At the user's request, an unpublished Zenodo draft reserved the identifier in
[the reservation receipt](../data/publication/zenodo-draft.json). That receipt
records the observed state at reservation; it is not a fresh server-state check.
The release metadata links the assigned identifier to its resolving DOI.
The historical reservation receipt remains unchanged; it describes the earlier
draft, not the release state. The release guide identifies the public record.
The pipeline neither reserves, uploads nor publishes a record.

## Automatic numbering and stable links

Each display equation has a stable `eq:` label, never an authored ordinal.
The registry hashes the expression and source order. The Pandoc Lua filter emits
native PDF equations and numbered HTML MathML with resolved references.

Each scientific image uses its own one-line block, stable `fig-` identifier
and a caption token from the shared catalog. The illustration registry binds
document order, image paths and resolved caption hashes. Figure numbers and
references are generated for both products. Missing, duplicate or unresolved
identifiers fail admission.

## Page geometry and readability

PDF margins, footer offset and body font are read from metadata and tested with
distinct real-render settings. PDF links are red, including citations, ORCID and
draft DOI. References use their separate readable type size and stay together
where feasible.

Page geometry includes the footer in the reserved page area. The offset must
accommodate the body font height plus two points of clearance; incompatible
metadata is rejected. Dense real-render tests check the body-to-page-number
gap on every generated test page, separately from physical page-edge bounds.

Scientific image placement uses the native width in
[visual_style.py](../src/thanks_for_nothing/visual_style.py), passed to the Lua
filter. A wider text block must not enlarge a portrait figure until its caption
falls outside the page. The portrait regression checks actual Poppler word
coordinates, and final inspection checks caption completeness and page numbers.
The PDF filter also caps image height at 83 percent of the reserved text height,
preserving aspect ratio and room for the caption. Inspect actual placement size
and typography after applying either width or height limits.

Figures remain in reading order. Tall blocks can leave whitespace before a page
break; this policy does not claim globally optimized pagination. Inspect the final
pages rather than inferring readable composition from a successful renderer.

The PDF filter keeps compact tables together so a page break cannot strand an
empty repeated header. This applies to tables with at most twelve rows including
headers and footers, and at most 1600 bytes of plain table text. Longer interval
and settings tables retain native pagination and repeated column headings.
Real-render regressions exercise short and long tables at a page boundary.
Compact tables use Pandoc's native `table` writer with `H` placement, keeping
their reading order. This requires Pandoc 3.10.1 or newer; older PDF writers fail
explicitly. CI installs checksum-pinned Pandoc 3.12.1 rather than the distribution
package. See the [upstream release notes](https://pandoc.org/releases.html) and
[native placement contract](https://pandoc.org/MANUAL.html#table-placement-in-latex).

## Qualification and delivery

The [publication build receipt](../output/reports/publication_build.json)
distinguishes the source used to generate current reader-facing products from
the historical numerical source receipt. It records whether rendering and
notebook execution occurred, and hashes the generated products. A build that
fails retains a `building` status, rather than a completed receipt.

An editorial rebuild can reuse an admitted numerical bundle through
`build_publication_products(root, output, read_bundle(output), notebook=False)`.
This regenerates GNN views, figures, the atlas, manuscript and documentation;
it does not regenerate simulated observations or execute companions. Preserve
the prior products first, verify retained numerical records and notebook
sources, and retain their original execution receipts. The new publication
receipt does not turn a historical full-pipeline validation into current
full-pipeline approval.

[Reproducibility](reproducibility.md) defines commands, source custody, two-runtime
tests, installed distributions and actual surface inspection.
[Visualization guidance](visualizations.md) specifies keys, uncertainty and
caption responsibilities. The independent release reviewer must approve the
exact commit they did not build. GitHub delivery remains separate from
Zenodo publication and from any empirical scientific claim.
