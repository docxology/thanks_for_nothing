# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace

from thanks_for_nothing.artifacts import write_record
from thanks_for_nothing.boundary_design import load_boundary_task
from thanks_for_nothing.boundary_figures import (
    boundary_allocation,
    boundary_convergence,
    boundary_information,
    boundary_outcomes,
    boundary_structure,
)
from thanks_for_nothing.boundary_findings import (
    boundary_findings,
    boundary_interval_table,
    boundary_upstream_findings,
)
from thanks_for_nothing.boundary_paths import boundary_paths
from thanks_for_nothing.boundary_upstream import build_boundary_upstream
from thanks_for_nothing.gaze_art import copy_artwork


def test_upstream_full_covariance_and_normalized_negative_control():
    audit = build_boundary_upstream()
    assert audit == build_boundary_upstream()
    assert audit.all_controls_pass
    assert all(audit.controls.values())
    assert audit.covariance_inverse_error < 1e-12
    assert audit.exhaustive_marginal_best_f1 == 0.8
    assert audit.precision_support_f1 == audit.partial_correlation_best_f1 == 1
    assert len(audit.qrf_distributions) == 3
    assert all(len(row[1]) == 64 for row in audit.qrf_distributions)
    assert len(audit.specification_sha256) > 40
    assert "does not imply" in boundary_upstream_findings(audit)
    assert "failed" in boundary_upstream_findings(replace(audit, all_controls_pass=False))


def test_source_bound_figures_and_complete_table(small_boundary, tmp_path):
    directory, audit = small_boundary
    upstream = build_boundary_upstream()
    write_record(tmp_path / "data/boundary_gaze.json", audit)
    write_record(tmp_path / "data/boundary_upstream.json", upstream)
    write_record(tmp_path / "data/gaze.json", {"model_sha256": audit.gaze_model_sha256})
    copy_artwork(None, tmp_path)
    output = tmp_path / "figures"
    figures = (
        boundary_information(audit, output),
        boundary_outcomes(audit, output),
        boundary_allocation(audit, output),
        boundary_convergence(audit, output),
        boundary_structure(upstream, output),
        boundary_paths(audit, load_boundary_task(directory).gaze.design, output),
    )
    assert len({f.name for f in figures}) == 6
    assert all(f.publication_min_font_points >= 10 for f in figures)
    assert (
        len([line for line in boundary_interval_table(audit).splitlines() if line.startswith("| ")])
        == 86
    )
    assert "reference-frame intervention" in boundary_findings(audit)
    assert "failed" in boundary_findings(replace(audit, all_controls_pass=False))
    first = audit.region.intervals[0]
    partial = replace(
        audit,
        region=replace(
            audit.region,
            intervals=(
                replace(first, low=None, high=None, status="unavailable_constant"),
                *audit.region.intervals[1:],
            ),
        ),
    )
    assert "Unavailable" in boundary_interval_table(partial)
    assert "unavailable" in boundary_findings(partial)
    assert boundary_outcomes(partial, output).name == "boundary_gaze_outcomes"
