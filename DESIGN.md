# Visual design contract

The executable design authority is
[`visual_style.py`](src/thanks_for_nothing/visual_style.py), with semantic tokens
and the required figure inventory in [`visual_tokens.py`](src/thanks_for_nothing/visual_tokens.py).
Its semantic roles are shared across the entire figure suite; do not choose
new colors independently in individual plotting functions.

| Role | Color | Meaning |
| --- | --- | --- |
| No recall | `#596579` | Paired reference condition |
| Positive recall | `#007C83` | Selected positive-event rehearsal |
| Matched random recall | `#B66A18` | Dose-matched comparator |
| Absence appreciation | `#8660A7` | Valuation with unchanged belief learning |
| Ink | `#142E3A` | Text and structure |
| Grid | `#E2E8EC` | Subordinate guides |
| Harm | `#B74343` | Adverse or negative-valence quantities |
| Artwork overlay | `#FFFFFF` | Sampled paths on the licensed painting, with dark outline |

Use DejaVu Sans, constrained layout and explicit axis units. The base type scale
is 11 points for text, 10 for ticks and legends, and 13 for titles. Export raises
visible text to retain at least **9.5 points at the 166 mm manuscript placement
width**, with a 10.5-point working minimum for a rounding margin. Both export and
placement font sizes are recorded. Pair color with labels and, where useful,
line styles; color alone must not identify a contrast. Quantitative sensitivity
maps use the declared `BrBG` diverging scale centered on zero, rather than
assigning a categorical intervention color to a numerical contrast.

Export each figure as both 220-dpi PNG and text-preserving SVG. `FigureRecord`
records dimensions, export and placement minimum font sizes, source-artifact paths/SHA256s, and both
image hashes. Export requires nonempty source files. Retain the figure source map
and inspect the real PNG/SVG/PDF outputs; a font-size check does not prove that
labels are unclipped or that a composed page is readable.

The views cover concepts, ensemble learning trajectories, predictive
loss by world, primary contrasts, paired-unit spread, world-weight sensitivity,
valuation nulls, absence information, policy masses, parameter sensitivity and
statistical operating characteristics, practice activity/access and conditional
revision, exhaustive count decisions, exact source gaze, learned-channel transfer
and active visual inquiry, the enacted mechanism, joint uncertainty and family
coverage, foundational task settings and the joint scene/encoding setting. Learning
trajectories retain every independent unit; means, unit IQRs and paired differences
occupy separate panels. Illustrative scanpaths remain single-unit examples. Show intervals and
sample units wherever a plot summarizes independent agents.

The six boundary/gaze views distinguish conditional query information, scene
paths versus nonspatial questions, the global exploratory region, sampling and
cost, independent-N convergence, and the separate pinned Gaussian fixture.
Probability matrices use the shared sequential `cividis` scale on [0,1], with
numeric annotations and contrast-aware text. Signed matrices use `BrBG` with an
explicit symmetric scale. Boundary condition labels and palette-role aliases
live in `visual_tokens`; reuse of a color does not equate those conditions with
the recall interventions. Exact intervals, stochastic intervals and unavailable
constants use distinct markers. Descriptive allocation/cost means carry pooled
whole-unit IQR segments, distinct from confidence intervals and repeated decisions.

Render at the actual 6.54-inch manuscript width rather than shrinking a wide
canvas after font selection. Separate between-unit IQRs, pointwise confidence
intervals and conditional weighting ranges in different panels with explicit
captions. Primary contrasts show percentile circles and bootstrap t diamonds;
constant nulls retain a visible point and an explicitly unavailable t interval.
Loss contrasts are scaled by 1000 consistently in axes, tables and captions.
World-specific intervals are exploratory, not subgroup significance decisions.

Operating-characteristic coverage and null rejection occupy separate panels.
Show bootstrap t availability for every fixture and count unavailable intervals
as noncoverage. Reference lines indicate nominal .95 coverage and .05 rejection;
they are not thresholds retuned to make the output pass. Sensitivity panels use
separate zero-centered numerical scales for different endpoint units.

Binary Brier score and predictive NLL are losses: **lower is better**. A positive
Brier change can be adverse even when the optimism readout rises. Describe
attention bars as model policy probability, not observed human gaze. Label
sensitivity as conditional on the finite parameter grid, and statistical
calibration as synthetic operating characteristics, not clinical power.

Concept diagrams must keep observed absence, missing evidence, counterfactual
valuation and representational invariance separate. Arrows express declared
computational dependencies, not established psychological or contemplative
causation. No figure may turn a software control into a human efficacy claim.

Figure 1 gives each distinction a symbolic setting: a functioning detector and
absence, an unavailable record, a counterfactual bracket, and a constructed
self/world boundary that remains open to examination. The Realizing Emptiness
panel depicts conditional usefulness and revisability rather than a realization
score. `task_settings` and `boundary_task` read budgets and settings from the
admitted bundle, identify actions/observations/assessment targets, and distinguish
spatial samples from nonspatial encoding questions. Their fixed schematic layout
uses the shared typography and palette; it does not represent measured behavior.
The global export uses larger text, bold left-aligned titles and extra vertical
space. Boundary convergence uses distinct markers for policies; allocation uses
different markers for the two observation regimes.

Practice views reuse semantic tokens through explicit policy-role mappings.
Solid gray/hatched teal bars compare activity with effective access; labels identify
conditions and give means to two significant digits, including visible exact zeros.
Forecast curves are replicate means, not confidence bands. The separate forest
panel uses pointwise analytic intervals over paired replicate averages. Its units
are nats per observation and are not scaled by 1000. Sham and blocked-access
forecasts coincide with rigid forecasts exactly; captions disclose the overlap.

Exact-decision panels show every possible calibration count and both declared
process distributions. Markers distinguish the selected family; the zero line is
the equal-evidence boundary. Paired linear/logarithmic views repeat the same
binomial masses so modal mass and rare tails can both be read. Dotted vertical
boundaries are derived from adjacent counts with different family selections;
they are not significance thresholds. Binomial masses are probability
distributions, not confidence bands, posterior family probabilities or
repeated-policy rates. Rare conditional probabilities remain in scientific
notation in the associated tables and notebook. Activity/access and forecast
axes retain the full unit interval without empty legend headroom; all keys
occupy the dedicated footer.

The cover is conceptual artwork outside the scientific figure inventory. Its
provenance, AI attribution and source hash are recorded separately. Author,
ORCID and DOI status are typeset from common metadata. PDF and HTML mathematical
formalisms use automatic numbering, stable authored labels and resolved links.

PDF body margins, footer offset and body type size are admitted from manuscript metadata. The generated research summary records their current values. Scientific figures
use the native publication width declared in `visual_style.py` (about 166 mm),
leaving room for complete portrait figures and their captions on the same page.
Standalone HTML uses a 16-pixel body with reduced outer padding.
The renderer injects that width into the PDF filter; HTML figures remain responsive.
The font requirement applies at that actual placement. PDF hyperlinks, including citations, ORCID and draft DOI,
are red; HTML retains the semantic teal link color.

The canonical vocabulary is authored in `concepts.py` and serialized as
`data/concepts.json`: A observed absence, B missing observation, C counterfactual
value and D non-reification. Figure 1, the reading guide, the operation map and
relevant result plots reuse these names. Local task panels use lowercase letters
to distinguish them from the concept codes. The operation map reads actual
posterior, information, reference-value, paired-null and activity-cost fields;
its different units are explicit. D links to Realizing Emptiness as a finite
enabling counterpart, with realization left unmeasured. Color-role aliases do
not equate concepts with the recall conditions using those colors.

Painting figures retain the whole portrait, use straight sampled segments and
mark first/last displayed locations. Source/transfer sequences include their
initial neutral location; active paths show sampled destinations. The original
JPEG and its CC BY 4.0 credit remain source-hashed. New transfer and gaze losses
use native nats per outcome, and probability changes use explicitly labeled
percentage points in figures. Gaze forest panels use pointwise analytic t
intervals; exact constant contrasts have zero-width analytic intervals, while
unavailable bootstrap t intervals remain explicit in the complete tables. Context,
support access and policy are distinguished by labels, not color alone.

The joint uncertainty view compares gray pointwise analytic circles with teal
joint-bootstrap diamonds. Purple squares identify mechanism-exact zeros; crosses
identify unavailable intervals. Separate axes retain native loss units and make
direct open-policy comparisons readable. The critical value comes from the entire
58-contrast exploratory family, including comparisons absent from the selected
view. Coverage and availability occupy separate panels with explicit independent-
experiment denominators; a nominal line is not a gate. The mechanism map uses a
dashed unmeasured appreciation link and solid computational-dependency arrows.

## Situated main results and visible keys

Main results pair an explicit cognitive task with selected quantitative readouts.
The situation panels show the source of observations, the agent's belief or working
family, its available actions, and what is assessed independently. Diagram positions
are schematic; arrows express declared computation, not measured human causation.
All budgets, cohort sizes and displayed estimates come from the admitted records.

| Main view | Situation | Quantitative readout | Complete supplementary comparisons |
| --- | --- | --- | --- |
| `recall_situation` | Shared experience, learned belief, matched replay, separate new tests | World-specific optimism and Brier changes | `paired_contrasts`, `calibration_by_world`, unit spread and world weights |
| `practice_situation` | Declared value, costly activity, access, retain/revise, independent prediction | Reversal forecasts and policy-minus-rigid loss | Both contexts, all policies, activity/access bars and exact decisions |
| `gaze_situation` | Scene locations, observations, belief and next-location policy | Attention transfer and direct inquiry-versus-open comparisons | Both bridges, full joint bounds, paths and operating checks |
| `boundary_situation` | Scene and encoding jointly determine evidence; two query types share a budget | Reference risk and encoding Brier in the existing excluded-encoding example | All encodings, controls, allocation, costs and convergence |

Every figure carries a visible **Key** in a reserved footer. Actual labeled plot
artists supply their own colors and line/marker styles; `legend_entries.py` adds
essential meanings for symbols, intervals, shading and diagrams. The footer adds
physical height rather than reducing panel typography. Color bars have explicit
quantity labels. Palette aliases are scoped to the named experiment or panel;
reusing a hue does not equate a concept, policy and interval method.

Export wraps titles at their actual panel width and rejects visible text outside
the image. Hidden axes and locator ticks outside the rendered view are excluded
from that test. Source-map records include every legend label, and the integrity
gate reads the actual vector key and palette. Removing or relabeling a key, or
introducing an undeclared color, fails even if image hashes are repaired.
`main_results_figure_context` separately enforces main/supplement placement.
Physical clearance and font checks complement inspection of every final image
and composed PDF page; they do not establish absence of internal overlap.

The experimental overview and technical crosswalk share one question registry.
Each row states the controlled manipulation, assessment and decisive control;
independent-unit labels come from the executed designs. Gaze situation readouts
use stacked full-width panels so long comparator labels do not squeeze the
scene diagram or numeric ticks. The caption catalog supplies task, reading,
uncertainty and scope fields for every scientific image. Numerical caption
values are admitted through the same producer-bound composition as body text.
