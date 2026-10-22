# Copyright (c) 2026 Daniel Ari Friedman
"""Hydrate source-grounded findings and render manuscript products."""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final

from pydantic import BaseModel, ConfigDict

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.boundary_findings import (
    boundary_findings,
    boundary_interval_table,
    boundary_upstream_findings,
)
from thanks_for_nothing.bundle import ResearchBundle
from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.experiment_overview import experiment_logic_table
from thanks_for_nothing.findings import (
    calibration_findings,
    heterogeneity_findings,
    interval_findings,
    main_findings,
)
from thanks_for_nothing.formalisms import build_formalism_registry
from thanks_for_nothing.gaze_findings import (
    gaze_interval_findings,
    gaze_joint_findings,
    gaze_joint_interval_findings,
    gaze_main_findings,
    gaze_source_findings,
    joint_calibration_findings,
)
from thanks_for_nothing.gnn_model_card import write_gnn_model_card
from thanks_for_nothing.graphical_abstracts import write_graphical_abstracts
from thanks_for_nothing.illustrations import build_illustration_registry
from thanks_for_nothing.manuscript_composition import compose_source
from thanks_for_nothing.practice_findings import (
    exact_decision_findings,
    practice_findings,
    practice_interval_findings,
)
from thanks_for_nothing.publication import load_publication, write_cover_header
from thanks_for_nothing.source_yarbus import YARBUS_RECONSTRUCTION_SEED, YARBUS_RECONSTRUCTION_STEPS
from thanks_for_nothing.visual_style import PUBLICATION_WIDTH_INCHES

SOURCE_DATE_EPOCH: Final = "1792108800"


class _SourceSummary(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    raw_counts_posterior_well: float
    normalized_posterior_well: float
    snapshot_mutation_max: float
    plot_excluded_grid_points: int


class _YarbusSummary(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    observation_process_mismatch_count: int
    efe_ambiguity_cost_oracle_max_error: float


@dataclass(frozen=True, slots=True)
class Replacement:
    """A manuscript template token and its generated source-bound prose."""

    token: str
    text: str


def hydration(bundle: ResearchBundle) -> tuple[Replacement, ...]:
    """Build typed prose replacements from the exact generated research bundle."""
    source = _SourceSummary.model_validate(bundle.source["controls"])
    yarbus = _YarbusSummary.model_validate(bundle.source["yarbus"]["controls"])
    calibration_text = calibration_findings(bundle.calibration)
    attention_text = "\n\n".join(
        " ".join(
            (
                f"The {row.condition.replace('attention_', '')} precision model assigned mean",
                f"policy probability {row.positive_mass:.4f} to positive, {row.neutral_mass:.4f}",
                f"to neutral, and {row.negative_mass:.4f} to negative locations",
                f"over {len(row.actions)} steps.",
            )
        )
        for row in bundle.attention.rows
    )
    rows = bundle.sensitivity.rows
    if not rows:
        message = "Sensitivity findings require at least one admitted grid cell"
        raise ContractError(message)
    optimism = tuple(row.optimism_positive_minus_random for row in rows)
    brier = tuple(row.brier_positive_minus_random for row in rows)
    sensitivity_text = " ".join(
        (
            f"Across {len(rows)} separately admitted grid cells, the positive-minus-random",
            f"optimism change contrast ranged from {min(optimism):.5f} to {max(optimism):.5f};",
            f"the corresponding Brier contrast ranged from {min(brier):.5f} to {max(brier):.5f}.",
            f"Each cell used {bundle.study.design.sensitivity_replicates} independent agents per",
            "fixed stratum, sharing seeds across cells.",
        )
    )
    source_text = " ".join(
        (
            "An independent unequal-column-mass example returned posterior well probability",
            f"{source.raw_counts_posterior_well:.4f} from raw counts versus",
            f"{source.normalized_posterior_well:.4f} after column normalization.",
            "The seeded source adapter measured a maximum aliased snapshot mutation of",
            f"{source.snapshot_mutation_max:.4f}. The original plot binning excluded",
            f"{source.plot_excluded_grid_points} endpoint-grid agent(s). In the attention",
            f"reconstruction (seed {YARBUS_RECONSTRUCTION_SEED}, {YARBUS_RECONSTRUCTION_STEPS} steps),",
            f"{yarbus.observation_process_mismatch_count} sampled observations had zero likelihood",
            "under the separately declared process. The independent preference-plus-ambiguity",
            "oracle matched the source energy to maximum absolute error",
            f"{yarbus.efe_ambiguity_cost_oracle_max_error:.3g}.",
        )
    )
    absence = bundle.nothingness
    absence_text = " ".join(
        (
            f"Missingness preserved the prior with KL divergence {absence.missing_kl_bits:.4f}",
            f"bits; an observed absence produced {absence.observed_absence_kl_bits:.4f} bits.",
            "The imported finite Blackwell comparator returned Bayes risk",
            f"{absence.blackwell_original_risk:.4f} for its original channel and",
            f"{absence.blackwell_erasure_risk:.4f} under erasure. These are separate declared finite",
            "comparators, not measured psychological or contemplative changes.",
        )
    )
    return (
        Replacement("{{EXPERIMENT_LOGIC_TABLE}}", experiment_logic_table(bundle)),
        Replacement("{{MAIN_FINDINGS}}", main_findings(bundle)),
        Replacement("{{HETEROGENEITY_FINDINGS}}", heterogeneity_findings(bundle.statistics)),
        Replacement("{{INTERVAL_FINDINGS}}", interval_findings(bundle)),
        Replacement("{{CALIBRATION_FINDINGS}}", calibration_text),
        Replacement("{{ATTENTION_FINDINGS}}", attention_text),
        Replacement("{{SENSITIVITY_FINDINGS}}", sensitivity_text),
        Replacement("{{SOURCE_FINDINGS}}", source_text),
        Replacement("{{NOTHINGNESS_FINDINGS}}", absence_text),
        Replacement("{{PRACTICE_FINDINGS}}", practice_findings(bundle.practice)),
        Replacement("{{EXACT_DECISION_FINDINGS}}", exact_decision_findings(bundle.exact_decision)),
        Replacement("{{PRACTICE_INTERVAL_FINDINGS}}", practice_interval_findings(bundle.practice)),
        Replacement("{{GAZE_SOURCE_FINDINGS}}", gaze_source_findings(bundle.gaze)),
        Replacement("{{GAZE_MAIN_FINDINGS}}", gaze_main_findings(bundle.gaze)),
        Replacement("{{GAZE_INTERVAL_FINDINGS}}", gaze_interval_findings(bundle.gaze)),
        Replacement("{{GAZE_JOINT_FINDINGS}}", gaze_joint_findings(bundle.gaze_uncertainty)),
        Replacement(
            "{{JOINT_CALIBRATION_FINDINGS}}", joint_calibration_findings(bundle.gaze_uncertainty)
        ),
        Replacement(
            "{{GAZE_JOINT_INTERVAL_FINDINGS}}",
            gaze_joint_interval_findings(bundle.gaze, bundle.gaze_uncertainty),
        ),
        Replacement("{{BOUNDARY_GAZE_FINDINGS}}", boundary_findings(bundle.boundary_gaze)),
        Replacement("{{BOUNDARY_INTERVAL_TABLE}}", boundary_interval_table(bundle.boundary_gaze)),
        Replacement(
            "{{BOUNDARY_UPSTREAM_FINDINGS}}", boundary_upstream_findings(bundle.boundary_upstream)
        ),
    )


def compose_manuscript(root: Path, output: Path, bundle: ResearchBundle) -> Path:
    """Hydrate the manuscript and bind its figure paths to the artifact directory."""
    source, ledger = compose_source(
        root, output, bundle, {row.token: row.text for row in hydration(bundle)}
    )
    path = output / "reports/manuscript.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(source)
    write_record(output / "reports/manuscript_variables.json", ledger)
    write_record(output / "reports/formalisms.json", build_formalism_registry(source))
    write_record(output / "reports/illustrations.json", build_illustration_registry(source))
    return path


def render_manuscript(
    root: Path, output: Path, manuscript: Path, *, graphical_abstracts: bool | None = None
) -> tuple[Path, ...]:
    """Render PDF and standalone HTML; retain subprocess output on success or failure."""
    metadata = load_publication(root)
    include_abstracts = (
        metadata.graphical_abstracts if graphical_abstracts is None else graphical_abstracts
    )
    abstracts = (
        (*write_graphical_abstracts(root, output), write_gnn_model_card(output))
        if include_abstracts
        else ()
    )
    cover = write_cover_header(
        root, output, tuple((output / page.pdf, page.links) for page in abstracts)
    )
    common = [
        "pandoc",
        str(manuscript),
        "--standalone",
        "--number-sections",
        "--toc",
        "--toc-depth=2",
        "--citeproc",
        "--bibliography",
        str(root / "docs/manuscript/references.bib"),
        "--metadata-file",
        str(root / "docs/manuscript/metadata.yaml"),
        "--metadata",
        f"doi-display={metadata.doi_display}",
        "--metadata",
        f"doi-url={metadata.doi_url or ''}",
        *(
            item
            for page in abstracts
            for item in (
                "--metadata",
                f"graphical-abstract-{page.key}-image={(output / page.svg).resolve()}",
                "--metadata",
                f"graphical-abstract-{page.key}-title={page.title}",
                "--metadata",
                f"graphical-abstract-{page.key}-alt={page.alt}",
            )
        ),
        "--resource-path",
        str(root),
        "--lua-filter",
        str(root / "docs/manuscript/filters/formalisms.lua"),
    ]
    environment = os.environ | {"SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH, "FORCE_SOURCE_DATE": "1"}
    targets: tuple[tuple[str, list[str]], ...] = (
        (
            "manuscript.pdf",
            [
                "--pdf-engine=xelatex",
                "--metadata",
                f"publication-figure-width={PUBLICATION_WIDTH_INCHES}in",
                "--include-in-header",
                str(cover),
                "-V",
                (
                    f"geometry:includefoot,margin={metadata.pdf_margin_mm:g}mm,"
                    f"footskip={metadata.pdf_footer_offset_mm:g}mm"
                ),
                "-V",
                f"fontsize={metadata.pdf_body_font_pt:g}pt",
                "-V",
                "papersize=a4",
                "-V",
                "colorlinks=true",
                "-V",
                "linkcolor=red",
                "-V",
                "urlcolor=red",
                "-V",
                "citecolor=red",
                "-V",
                "filecolor=red",
            ],
        ),
        (
            "manuscript.html",
            [
                "--embed-resources",
                "--math-method=mathml",
                "--template",
                str(root / "docs/manuscript/templates/manuscript.html"),
            ],
        ),
    )
    logs: list[str] = []
    paths: list[Path] = []
    log = output / "reports/render.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    for name, options in targets:
        target = output / name
        result = subprocess.run(  # noqa: S603 - explicit executable and argument vector, no shell
            [*common, *options, "--output", str(target)],
            cwd=root,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        logs.append(f"{name}\n{result.stdout}{result.stderr}")
        _ = log.write_text("\n\n".join(logs))
        if result.returncode:
            message = f"Manuscript render failed for {name}; see {log}"
            raise ContractError(message)
        paths.append(target)
    return tuple(paths)
