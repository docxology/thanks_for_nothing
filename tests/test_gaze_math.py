# Copyright (c) 2026 Daniel Ari Friedman
from math import log

import numpy as np
import pytest

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.finite_evidence import fit_finite_evidence
from thanks_for_nothing.gaze_math import balanced_scene_loss, categorical_samples, region_prediction


def test_inverse_cdf_excludes_zero_mass_at_boundary():
    probabilities = np.array([0.0, 0.4, 0.0, 0.6, 0.0])
    uniforms = np.array([0.0, 0.4, np.nextafter(1.0, 0.0)])
    assert categorical_samples(probabilities, uniforms).tolist() == [1, 3, 3]


def test_finite_evidence_known_answer():
    terms, posterior, evidence, error = fit_finite_evidence(
        np.array([0.25, 0.75]),
        np.log(np.array([0.8, 0.2])),
    )
    assert posterior == pytest.approx([4 / 7, 3 / 7])
    assert evidence == pytest.approx(-log(0.35))
    assert terms.free_energy == pytest.approx(evidence)
    assert error < 1e-14


@pytest.mark.parametrize(
    ("prior", "likelihood"),
    [
        ([0.0, 0.0], [0.0, 0.0]),
        ([0.2, 0.3], [0.0, 0.0]),
        ([-0.1, 1.1], [0.0, 0.0]),
        ([0.5, 0.5], [float("nan"), 0.0]),
        ([0.5, 0.5], [0.0]),
    ],
)
def test_finite_evidence_rejects_invalid_input(prior, likelihood):
    with pytest.raises(ContractError, match="Finite evidence"):
        fit_finite_evidence(np.array(prior), np.array(likelihood))


def test_information_gain_known_answer_and_semantic_null():
    channels = np.array([[[0.9, 0.1], [0.1, 0.9]], [[0.8, 0.8], [0.2, 0.2]]])
    predictions, information = region_prediction(channels, np.array([0.5, 0.5]))
    assert predictions == pytest.approx(np.array([[0.5, 0.5], [0.8, 0.2]]))
    binary_entropy = -0.9 * log(0.9) - 0.1 * log(0.1)
    assert information == pytest.approx([log(2) - binary_entropy, 0.0], abs=1e-14)
    assert balanced_scene_loss(predictions.T, predictions.T) == pytest.approx(
        (log(2) - 0.8 * log(0.8) - 0.2 * log(0.2)) / 2,
    )
