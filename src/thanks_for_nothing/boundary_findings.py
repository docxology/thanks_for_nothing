# Copyright (c) 2026 Daniel Ari Friedman
"""Generate bounded prose and the complete intersection family directly from admitted results."""

from thanks_for_nothing.boundary_contracts import BoundaryGazeAudit
from thanks_for_nothing.boundary_upstream import BoundaryUpstreamAudit
from thanks_for_nothing.joint_contracts import JointInterval
from thanks_for_nothing.visual_tokens import BOUNDARY_LABELS


def _bounds(row: JointInterval) -> str:
    return "unavailable" if row.low is None or row.high is None else f"[{row.low:.5f}, {row.high:.5f}]"


def boundary_findings(audit: BoundaryGazeAudit) -> str:
    """Report all six policies on the same explicit reference intervention without choosing a winner."""
    indexed = {row.key: row for row in audit.region.intervals}
    lines = [
        (
            f"The joint experiment used {len(audit.episodes) // len(audit.design.conditions)} "
            f"independent paired units across "
            f"{len(audit.design.regimes) * len(audit.design.scene_maps) ** 2} "
            f"fixed regime/scene/encoding cells, with "
            f"{audit.design.replicates} replicates per cell and {audit.design.steps} decisions "
            f"per episode. The {len(audit.episodes)} policy episodes are repeated conditions on "
            f"those units, not additional independent agents."
        ),
        (
            "Diagnostic-regime anchored excess-log-loss differences (first policy minus "
            "visual-only; nats per outcome) were:"
        ),
    ]
    for condition in audit.design.conditions:
        if condition == "visual":
            continue
        results: list[str] = []
        for h in range(len(audit.design.scene_maps)):
            row = indexed[f"diagnostic/H{h}/{condition}/visual/anchored_regret"]
            bounds = (
                "unavailable"
                if row.low is None or row.high is None
                else f"[{row.low:.5f}, {row.high:.5f}]"
            )
            results.append(f"H{h}: {row.mean:.5f} {bounds}")
        lines.append(f"{BOUNDARY_LABELS[condition]}: " + "; ".join(results) + ".")
    for reference in ("uniform", "boundary_only"):
        for endpoint in audit.design.endpoints:
            estimates = [
                indexed[f"diagnostic/H{h}/integrated/{reference}/{endpoint}"]
                for h in range(len(audit.design.scene_maps))
            ]
            values = "; ".join(f"H{h}: {row.mean:.5f} {_bounds(row)}" for h, row in enumerate(estimates))
            lines.append(
                f"Integrated minus {BOUNDARY_LABELS[reference]}, {endpoint.replace('_', ' ')}: {values}."
            )
    region = audit.region
    estimated = sum(row.status == "estimated" for row in region.intervals)
    exact = sum(row.status == "mechanism_exact" for row in region.intervals)
    unavailable = sum(row.status == "unavailable_constant" for row in region.intervals)
    lines.append(
        "".join(
            (
                f"The separate {len(region.intervals)}-contrast exploratory family retained ",
                f"{estimated} stochastic ",
                f"estimates, {exact} mechanism-exact constants and {unavailable} unavailable sample ",
                f"constants. Bounds use one {100 * region.confidence:.0f}% ",
                "original-standard-error-standardized empirical-bootstrap maximum across all ",
                f"{len(region.blocks)} ",
                f"independent regime/H blocks, with {region.draws} resamples. They do not establish ",
                "finite-sample coverage or human construct validity.",
            )
        )
    )
    if (
        region.critical_value is not None
        and region.critical_mc_low is not None
        and region.critical_mc_high is not None
    ):
        lines.append(
            "".join(
                (
                    f"The conditional critical value was {region.critical_value:.4f}; its ",
                    f"{100 * region.monte_carlo_confidence:.0f}% order-statistic Monte Carlo bracket ",
                    f"was [{region.critical_mc_low:.4f}, {region.critical_mc_high:.4f}]. This bracket ",
                    "concerns bootstrap simulation error, not an additional effect interval.",
                )
            )
        )
    offsets = "; ".join(
        f"H{h}: {indexed[f'label_only/H{h}/restricted/visual/boundary_brier'].mean:+.6g}"
        for h in range(len(audit.design.scene_maps))
    )
    exact_identity_sentences = (
        "In the label-only regime, every boundary posterior retained its admitted prior. The",
        f"restricted-prior Brier differences were {offsets},",
        "with mechanism-exact bounds; other label-only Brier differences were zero.",
        "Boundary-only inquiry retained the uniform scene posterior. These identities",
        "distinguish information, support and joint use of scene/encoding evidence;",
        "posterior entropy is not metacognitive sensitivity.",
    )
    lines.append(" ".join(exact_identity_sentences))
    lines.append(
        "".join(
            (
                f"All {len(audit.controls)} independent mathematical/admission controls ",
                f"{'passed' if audit.all_controls_pass else 'failed'}. The sham is a nonautonomous ",
                "matched-query updater that discards action identity and ignores adaptive-schedule ",
                "information. The anchored H=0 score is a declared reference-frame intervention, not ",
                "ordinary future prediction under the original scene process.",
            )
        )
    )
    return "\n\n".join(lines)


def boundary_interval_table(audit: BoundaryGazeAudit) -> str:
    """Retain every declared member and exact nonzero offset in a compact, auditable table."""
    lines = [
        "| Regime / H | Contrast | Endpoint | Mean | Joint interval | Status |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in audit.region.intervals:
        regime, h, condition, reference, endpoint = row.key.split("/")
        comparison = f"{BOUNDARY_LABELS[condition]} - {BOUNDARY_LABELS[reference]}"
        bounds = (
            "Unavailable" if row.low is None or row.high is None else f"[{row.low:.6f}, {row.high:.6f}]"
        )
        lines.append(
            "".join(
                (
                    f"| {regime.replace('_', ' ')} / {h} | {comparison} | ",
                    f"{'Anchor loss' if endpoint == 'anchored_regret' else 'Boundary Brier'} | ",
                    f"{row.mean:.6f} | {bounds} | {row.status.replace('_', ' ')} |",
                )
            )
        )
    return "\n".join(lines)


def boundary_upstream_findings(audit: BoundaryUpstreamAudit) -> str:
    """State the narrow, independently reproduced upstream result and its interpretation limit."""
    return (
        f"The pinned QRF audit assigned the same complete "
        f"{len(audit.qrf_distributions[0][1])}-outcome distribution to "
        f"{len(audit.qrf_distributions)} label profiles; this equality is constructed, not fitted "
        f"from observations. A normalized altered distribution was detected independently. In a "
        f"separate six-variable Gaussian fixture, precision-support F1 was "
        f"{audit.precision_support_f1:.2f}, partial-correlation best F1 "
        f"{audit.partial_correlation_best_f1:.2f}, and the best F1 across every possible "
        f"marginal-correlation threshold interval was {audit.exhaustive_marginal_best_f1:.2f}. "
        f"Inverting the known full covariance recovered precision to maximum error "
        f"{audit.covariance_inverse_error:.3g}. Thus the threshold limitation does not imply "
        f"general non-identifiability from joint observations. The upstream perturbation audit "
        f"retained {audit.positive_definite_samples}/{audit.perturbation_samples} "
        f"positive-definite draws; its recovery fractions are conditional on that admission. "
        f"These fixtures and the new sampled structural-inquiry experiment test different "
        f"mathematical claims. All {len(audit.controls)} upstream integration and independent "
        f"mathematical controls {'passed' if audit.all_controls_pass else 'failed'}; actual "
        f"module, declaration and serialized-API digests are retained."
    )
