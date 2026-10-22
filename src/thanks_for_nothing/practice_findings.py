# Copyright (c) 2026 Daniel Ari Friedman
"""Hydrate all practice-extension comparisons without selecting favorable results."""

from thanks_for_nothing.practice_contracts import ExactDecisionAudit, PracticeAudit
from thanks_for_nothing.visual_tokens import PRACTICE_LABELS as NAMES


def practice_findings(audit: PracticeAudit) -> str:
    """Separate policy implementation from prediction at the replicate level."""
    design = audit.design
    level = 100 * audit.contrasts[0].heldout_loss_difference.confidence
    opening = (
        f"The separate practice extension used {design.replicates} independent paired replicates "
        f"per context and {len(design.contexts[0].probabilities)} repeated windows per replicate. "
        f"Each window contained {design.calibration_samples} calibration observations and "
        f"{design.assessment_samples} independently generated assessment observations. "
        "Intervals resample replicate averages; repeated windows are not treated as independent units."
    )
    lines = [
        opening,
        "",
        "| Context / policy | Chosen activity | Effective access | Cost / window |",
        "| --- | ---: | ---: | ---: |",
    ]
    lines.extend(
        "".join(
            (
                f"| {row.context.capitalize()} / {NAMES[row.condition]} ",
                f"| {row.mean_practice_rate:.3f} | {row.mean_access_rate:.3f} | {row.mean_cost:.3f} |",
            )
        )
        for row in audit.contrasts
    )
    lines.extend(
        (
            "",
            f"| Context / policy | Loss difference | Analytic t {level:g}% interval |",
            "| --- | ---: | --- |",
        )
    )
    for row in audit.contrasts:
        interval = row.heldout_loss_difference
        lines.append(
            "".join(
                (
                    f"| {row.context.capitalize()} / {NAMES[row.condition]} | {interval.mean:+.4f} ",
                    f"| [{interval.analytic_low:+.4f}, {interval.analytic_high:+.4f}] |",
                )
            )
        )
    lines.extend(
        (
            "",
            (
                "Loss differences are policy minus rigid, in nats per held-out observation; "
                "negative values favor the policy. All intervals are pointwise and exploratory, "
                "outside the original primary Holm family. Cost is a declared utility charge, "
                "reported separately rather than subtracted from predictive loss. The supplement "
                "reports percentile and studentized bootstrap intervals "
                f"for all {len(audit.contrasts)} contrasts."
            ),
            "",
            "All finite mathematical and semantic controls passed."
            if audit.all_controls_pass
            else "One or more finite controls failed; inspect emptiness_practice.json.",
        )
    )
    return "\n".join(lines)


def practice_interval_findings(audit: PracticeAudit) -> str:
    """Retain all practice interval families, including unavailable studentized intervals."""
    level = 100 * audit.contrasts[0].heldout_loss_difference.confidence
    lines = [
        f"| Context / policy | Percentile {level:g}% | Bootstrap t {level:g}% | Analytic t {level:g}% |",
        "| --- | --- | --- | --- |",
    ]
    for row in audit.contrasts:
        interval = row.heldout_loss_difference
        studentized = interval.studentized
        match studentized.status:
            case "available":
                if studentized.low is None or studentized.high is None:
                    message = "Available studentized interval requires both bounds"
                    raise ValueError(message)
                boot = f"[{studentized.low:+.4f}, {studentized.high:+.4f}]"
            case "degenerate_sample" | "degenerate_resamples":
                boot = f"Unavailable ({studentized.status.replace('_', ' ')})"
        lines.append(
            "".join(
                (
                    f"| {row.context.capitalize()} / {NAMES[row.condition]} ",
                    f"| [{interval.percentile_low:+.4f}, {interval.percentile_high:+.4f}] ",
                    f"| {boot} | [{interval.analytic_low:+.4f}, {interval.analytic_high:+.4f}] |",
                )
            )
        )
    return "\n".join(lines)


def exact_decision_findings(audit: ExactDecisionAudit) -> str:
    """Report conditional enumeration without rounding a rare selection probability to zero."""
    selected = ", ".join(str(row.zero_count) for row in audit.rows if row.supports_open) or "none"
    lines = [
        "".join(
            (
                f"The exhaustive analysis covered all {len(audit.rows)} counts in a window of ",
                f"{audit.calibration_samples} observations. The open family was selected for ",
                f"channel-0 counts {selected}; exact ties retain the restriction.",
            )
        ),
        "",
        "| Process probability | P(select open) | Expected loss difference |",
        "| ---: | ---: | ---: |",
    ]
    lines.extend(
        "".join(
            (
                f"| {point.process_probability:g} | {point.open_probability:.9g} ",
                f"| {point.expected_loss_difference:+.9g} |",
            )
        )
        for point in audit.operating_points
    )
    lines.extend(
        (
            "",
            """These are conditional on an effective inquiry with the stated calibration size.
The loss difference is evidence-selected minus restricted prediction in nats per
future observation, averaged over every possible calibration count. Probability
masses and selections use exact rational arithmetic; logarithms and loss values
are evaluated numerically. There is no Monte Carlo interval. Availability, policy
history, action cost and human parameter uncertainty are outside this calculation.""",
        )
    )
    return "\n".join(lines)
