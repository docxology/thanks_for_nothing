# Manuscript values and numerical provenance

Changing quantities enter the paper through producer-bound variables. Maintained
guides link to the [generated current facts](../output/reports/research_summary.md)
rather than repeating sample sizes, budgets, interval levels or publication counts.

## Authoring boundary

The graphical-abstract catalog uses the same scalar placeholders. Its renderer
reads the composed manuscript ledger, rejects unresolved or bare scientific
quantities, and binds both images to the catalog and ledger digests. The
symbolic equations are definitions reused from the concept diagrams, not
new measured outcomes. Cover identity, framing and revision date are declared
in publication metadata.

The main IMRAD text and technical supplement use `{{NAME}}` placeholders.
[The caption catalog](manuscript/captions.yaml) uses the same placeholders inside
required title, task, reading, uncertainty and scope fields. The composer expands
captions first, discovers their numerical dependencies, checks authored literals,
and then resolves values. Moving a quantity into a caption does not evade admission.

[Manuscript variables](../src/thanks_for_nothing/manuscript_variables.py) read typed
experiment records and the actual preserved GNN tensors. The
[additional quantity adapter](../src/thanks_for_nothing/manuscript_quantities.py)
binds boundary cardinalities, actual restricted support, excluded encodings,
exact process probabilities and artwork attribution. Historical transcriptions
have a separate source adapter; they never become simulated after-treatment data.

The [variable ledger](../output/reports/manuscript_variables.json) records every
used scalar's displayed value, producer path, source digest and selector. It also
binds authored component and caption hashes, generated findings, the canonical
bundle and final composed text. The composition gate replays these exact bindings.

## What the literal check permits

[Literal admission](../src/thanks_for_nothing/manuscript_literals.py) rejects bare
experimental counts, percentages, decimal probabilities and scientific notation.
It permits citation keys and locators, stable markup identifiers, named scripture
identifiers and fixed mathematical identities. Zero/one probability identities
and squared losses are definitions, not empirical estimates.

This lexical check cannot decide whether a philosophical interpretation is sound
or whether an author has disguised a number as words. Review still checks written
number words, source attribution, units, denominators and the meaning of generated
findings. The rule is to inject every changing scientific quantity, not merely
to satisfy a regular expression.

## Preserved model authority

Numerical model choices remain in [packaged GNN declarations](../src/thanks_for_nothing/models).
Their real upstream parser, admission and mathematical interfaces are exercised;
guide text and figure code must not supply an alternative default. Independent
known-answer fixtures retain their mathematical constants as controls rather
than being tuned to the fitted model.

Version, author, ORCID, draft DOI and PDF layout come from
[publication metadata](manuscript/metadata.yaml). Artwork identity comes from its
acquisition provenance. Bibliographic dates and discourse identifiers belong to
named editions; they are distinct from changing experiment settings.

## Tests that can reject a defect

Notebook execution injects the selected source root and output directory into
each kernel. All companions resolve their numerical declarations through the
same notebook context. An explicitly selected output without preserved models
fails; manual execution before a pipeline run may use the packaged declarations.
Paired-unit counts are derived from actual identities, and reconstruction size
comes from its selected analysis declaration.
The gaze companion also generates embedding dimensions, complete-location risk
scope, regional occupancy denominators, policy membership and structural support
from that selected admitted task. An exported-notebook test changes the real
scene and policy declarations and rejects the original numeric prose.

The GNN graphical-model views use the same admitted source bytes and derive
node/edge membership and tensor shapes from the parser and arrays. Native
attention dimensions follow those arrays, including in real source-edit tests.
The Gaussian comparator's precision color range and fixture-size annotation
follow its actual matrix; the correlation bound remains a mathematical identity.

Real tests alter a reduced admitted design and verify the resulting prose,
captions and tensor bindings. Other tests insert unbound counts, decimal and
scientific-notation values, forge ledger values or source hashes, mutate a
supplement, change an admitted tensor, remove a caption field, and introduce
unknown or duplicate tokens. Preserve failing receipts and rerun the affected
scenario after correction. Do not repair a stale number by copying another literal.

See [production](manuscript-production.md), [model authority](model-contract.md)
and [reproducibility](reproducibility.md).
