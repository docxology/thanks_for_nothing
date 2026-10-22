# Copyright (c) 2026 Daniel Ari Friedman
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise the installed distribution outside its source checkout with explicit external inputs."""

import argparse
from math import isclose
from pathlib import Path

from rich.console import Console

import thanks_for_nothing
from thanks_for_nothing.analysis_design import load_analysis
from thanks_for_nothing.bootstrap_availability import bernoulli_availability
from thanks_for_nothing.emptiness_practice import build_practice_audit
from thanks_for_nothing.estimation import StatisticalInputError
from thanks_for_nothing.experiments import run_learning_experiment
from thanks_for_nothing.gaze import build_gaze_audit
from thanks_for_nothing.nothingness import build_nothingness_audit
from thanks_for_nothing.provenance import SOURCE_PINS, build_provenance_audit, file_digest
from thanks_for_nothing.source_inputs import SourceInputError, source_bytes
from thanks_for_nothing.specifications import load_study


def require(condition: object, message: str) -> None:
    """Keep qualification checks active under optimized Python execution."""
    if not condition:
        raise RuntimeError(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    root = parser.parse_args().root.resolve()
    package = Path(thanks_for_nothing.__file__).resolve().parent
    require(not package.is_relative_to(root), "Qualification imported the checkout")
    for source in (root / "src/thanks_for_nothing").rglob("*"):
        if source.suffix in {".py", ".md"}:
            installed = package / source.relative_to(root / "src/thanks_for_nothing")
            require(file_digest(installed) == file_digest(source),
                    f"Installed source mismatch: {source}")
    for pin in SOURCE_PINS:
        resource = package / "resources/sources" / Path(pin.path).name
        if resource.suffix == ".ipynb":
            require(not resource.exists(), "Wheel redistributed an unlicensed source notebook")
        else:
            require(file_digest(resource) == pin.sha256, "Bundled preprint bytes changed")
    try:
        _ = source_bytes(None, "gratitude_original.ipynb")
    except SourceInputError:
        pass
    else:
        message = "Missing external input did not fail closed"
        raise RuntimeError(message)
    require(bool(build_provenance_audit(root).sources), "External source admission failed")
    model, design = load_study()
    require(bool(model.source_hash) and design.replicates > 0, "Packaged declaration failed")
    learning = run_learning_experiment(replicates=load_analysis().notebook_replicates)
    require(all(learning.study.controls.values()), "Learning controls failed")
    require(build_gaze_audit(learning, root=root).all_controls_pass, "Gaze controls failed")
    require(build_practice_audit(replicates=load_analysis().notebook_replicates).all_controls_pass,
            "Practice controls failed")
    require(build_nothingness_audit().all_controls_pass, "Absence controls failed")
    require(isclose(bernoulli_availability(2, 0.5, 2).exact_availability, 1 / 8,
                    rel_tol=0, abs_tol=1e-15),
            "Independent finite availability control failed")
    try:
        _ = bernoulli_availability(2, -0.1, 2)
    except StatisticalInputError:
        pass
    else:
        message = "Invalid probability was admitted"
        raise RuntimeError(message)
    Console().print({"package": str(package), "model_sha256": model.source_hash,
                     "external_root": str(root), "controls": "PASS"})
