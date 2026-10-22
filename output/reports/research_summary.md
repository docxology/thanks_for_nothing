# Current research facts

Generated from admitted records. Maintained guides link here for current quantities.

| Publication quantity | Value | Authority |
| --- | --- | --- |
| Version | 0.11.0 | docs/manuscript/metadata.yaml |
| Manuscript revision date | 2026-10-22 | docs/manuscript/metadata.yaml |
| PDF margins (mm) | 7 | pdf-margin-mm |
| PDF footer offset (mm) | 5 | pdf-footer-offset-mm |
| PDF body font (points) | 10 | pdf-body-font-pt |
| Scientific figures | 40 | reports/illustrations.json |
| Numbered equations | 29 | reports/formalisms.json |
| Scholarship sources | 107 | data/scholarship/sources.json |

## Executed design and independent units

Selectors distinguish independent replicates, repeated windows, episodes and decisions.

| Variable | Executed value | Producer | Selector |
| --- | --- | --- | --- |
| STUDY_SEED | 20261015 | data/study.json | /design/seed |
| STUDY_REPLICATES | 1024 | data/study.json | /design/replicates |
| STUDY_LUCKINESS | 0.1, 0.3, 0.5, 0.7, 0.9 | data/study.json | /design/luckiness |
| STUDY_BASELINE_DAYS | 7 | data/study.json | /design/baseline_days |
| STUDY_INTERVENTION_DAYS | 7 | data/study.json | /design/intervention_days |
| STUDY_STEPS_PER_DAY | 12 | data/study.json | /design/steps_per_day |
| STUDY_RECALL_COUNT | 3 | data/study.json | /design/recall_count |
| STUDY_RECALL_PRECISION | 4 | data/study.json | /design/recall_precision |
| STUDY_LEARNING_RATE | 2 | data/study.json | /design/learning_rate |
| STUDY_FORGETTING | 1 | data/study.json | /design/forgetting |
| STUDY_PRIOR_CONCENTRATION | 8 | data/study.json | /design/prior_concentration |
| STUDY_BOOTSTRAP_DRAWS | 8191 | data/study.json | /design/bootstrap_draws |
| STUDY_PERMUTATION_DRAWS | 8191 | data/study.json | /design/permutation_draws |
| STUDY_ASSESSMENT_TRIALS | 70 | data/study.json | /design/assessment_trials |
| STUDY_TASK_PRIOR_MIN | 0.05 | data/study.json | /design/task_prior_min |
| STUDY_TASK_PRIOR_MAX | 0.95 | data/study.json | /design/task_prior_max |
| STUDY_SENSITIVITY_REPLICATES | 128 | data/study.json | /design/sensitivity_replicates |
| STUDY_SENSITIVITY_PRIOR_CONCENTRATIONS | 1, 2, 8, 32, 128 | data/study.json | /design/sensitivity_prior_concentrations |
| STUDY_SENSITIVITY_RECALL_PRECISIONS | 0.25, 1, 4, 16, 64 | data/study.json | /design/sensitivity_recall_precisions |
| STUDY_CALIBRATION_REPLICATES | 4096 | data/study.json | /design/calibration_replicates |
| STUDY_CALIBRATION_SAMPLE_SIZE | 64 | data/study.json | /design/calibration_sample_size |
| STUDY_CALIBRATION_BOOTSTRAP_DRAWS | 1023 | data/study.json | /design/calibration_bootstrap_draws |
| STUDY_CALIBRATION_PERMUTATION_DRAWS | 1023 | data/study.json | /design/calibration_permutation_draws |
| STUDY_EVALUATION_TRIALS | 1024 | data/study.json | /design/evaluation_trials |
| STUDY_REFERENCE_HAZARD | 0.3 | data/study.json | /design/reference_hazard |
| STUDY_HARM_COST | 1 | data/study.json | /design/harm_cost |
| PRACTICE_SEED | 1729 | data/emptiness_practice.json | /design/seed |
| PRACTICE_REPLICATES | 512 | data/emptiness_practice.json | /design/replicates |
| PRACTICE_CALIBRATION_SAMPLES | 24 | data/emptiness_practice.json | /design/calibration_samples |
| PRACTICE_ASSESSMENT_SAMPLES | 512 | data/emptiness_practice.json | /design/assessment_samples |
| PRACTICE_BOOTSTRAP_DRAWS | 4095 | data/emptiness_practice.json | /design/bootstrap_draws |
| PRACTICE_ACTION_PRECISION | 6 | data/emptiness_practice.json | /design/action_precision |
| PRACTICE_PRACTICE_COST | 0.2 | data/emptiness_practice.json | /design/practice_cost |
| PRACTICE_EXAMINABILITY_PREFERENCE | 0.4 | data/emptiness_practice.json | /design/examinability_preference |
| PRACTICE_PREVIOUS_GAIN_WEIGHT | 1 | data/emptiness_practice.json | /design/previous_gain_weight |
| PRACTICE_METACOGNITIVE_ACCESS | 1 | data/emptiness_practice.json | /design/metacognitive_access |
| PRACTICE_PRIOR_PRECISION | 2 | data/emptiness_practice.json | /design/prior_precision |
| GAZE_SEED | 91073 | data/gaze.json | /design/seed |
| GAZE_SOURCE_SEED | 42 | data/gaze.json | /design/source_seed |
| GAZE_SOURCE_STEPS | 1000 | data/gaze.json | /design/source_steps |
| GAZE_SOURCE_RUNS | 5 | data/gaze.json | /design/source_runs |
| GAZE_TRANSFER_STEPS | 128 | data/gaze.json | /design/transfer_steps |
| GAZE_TRANSFER_AMBIGUITY_WEIGHT | 0.5 | data/gaze.json | /design/transfer_ambiguity_weight |
| GAZE_TRANSFER_PRECISION | 1.5 | data/gaze.json | /design/transfer_precision |
| GAZE_TRAJECTORY_STEPS | 20 | data/gaze.json | /design/trajectory_steps |
| GAZE_EXAMPLE_STRATA | 0.3, 0.7 | data/gaze.json | /design/example_strata |
| GAZE_EXAMPLE_WINDOW | 1 | data/gaze.json | /design/example_window |
| GAZE_REPLICATES | 512 | data/gaze.json | /design/replicates |
| GAZE_STEPS | 48 | data/gaze.json | /design/steps |
| GAZE_BOOTSTRAP_DRAWS | 4095 | data/gaze.json | /design/bootstrap_draws |
| GAZE_ACTION_PRECISION | 4 | data/gaze.json | /design/action_precision |
| GAZE_INFORMATION_WEIGHT | 4 | data/gaze.json | /design/information_weight |
| GAZE_SACCADE_COST | 0.2 | data/gaze.json | /design/saccade_cost |
| GAZE_STRUCTURAL_MODEL | emptiness_practice | data/gaze.json | /design/structural_model |
| GAZE_INITIAL_LOCATION | 10 | data/gaze.json | /design/initial_location |
| GAZE_REGIONS | 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2 | data/gaze.json | /design/regions |
| BOUNDARY_SEED | 620715 | data/boundary_gaze.json | /design/seed |
| BOUNDARY_REPLICATES | 512 | data/boundary_gaze.json | /design/replicates |
| BOUNDARY_STEPS | 24 | data/boundary_gaze.json | /design/steps |
| BOUNDARY_PREFIXES | 16, 32, 64, 128, 256, 512 | data/boundary_gaze.json | /design/prefixes |
| BOUNDARY_PROBE_RELIABILITIES | 0.65, 0.8, 0.95 | data/boundary_gaze.json | /design/probe_reliabilities |
| BOUNDARY_PROBE_COSTS | 0.02, 0.05, 0.1 | data/boundary_gaze.json | /design/probe_costs |
| BOUNDARY_ENDPOINTS | anchored_regret, boundary_brier | data/boundary_gaze.json | /design/endpoints |
| BOUNDARY_GAZE_MODEL | gaze | data/boundary_gaze.json | /design/gaze_model |
| BOUNDARY_ANCHOR_MAPPING | 0 | data/boundary_gaze.json | /design/anchor_mapping |
| BOUNDARY_JOINT_SEED | 620716 | data/boundary_gaze.json | /design/joint_seed |
| JOINT_SEED | 91074 | data/gaze_uncertainty.json | /design/seed |
| JOINT_DRAWS | 16383 | data/gaze_uncertainty.json | /design/draws |
| JOINT_CONFIDENCE | 0.95 | data/gaze_uncertainty.json | /design/confidence |
| JOINT_MONTE_CARLO_CONFIDENCE | 0.99 | data/gaze_uncertainty.json | /design/monte_carlo_confidence |
| JOINT_CALIBRATION_EXPERIMENTS | 4096 | data/gaze_uncertainty.json | /design/calibration_experiments |
| JOINT_CALIBRATION_UNITS | 64 | data/gaze_uncertainty.json | /design/calibration_units |
| JOINT_CALIBRATION_DRAWS | 1023 | data/gaze_uncertainty.json | /design/calibration_draws |
| AGENTS | 5120 | data/study.json | count(unique(rows.paired_id)) |
| REPLICATES | 1024 | data/study.json | /design/replicates |
| STUDY_STRATA | 5 | data/study.json | count(design.luckiness) |
| STUDY_CONDITIONS | 4 | data/study.json | count(unique(rows.condition)) |
| PRIMARY_CONTRASTS | 8 | data/statistics.json | count(contrasts) |
| PRACTICE_CONDITIONS | 5 | data/emptiness_practice.json | count(design.conditions) |
| PRACTICE_CONTEXTS | 2 | data/emptiness_practice.json | count(design.contexts) |
| PRACTICE_WINDOWS | 12 | data/emptiness_practice.json | count(design.contexts[0].probabilities) |
| PRACTICE_CONTRASTS | 8 | data/emptiness_practice.json | count(contrasts) |
| GAZE_LOCATIONS | 13 | data/gaze.json | count(design.coordinates) |
| GAZE_CONDITIONS | 6 | data/gaze.json | count(design.conditions) |
| GAZE_EPISODES | 18432 | data/gaze.json | count(episodes) |
| GAZE_CONTEXTS | 2 | data/gaze.json | count(design.contexts) |
| GAZE_REGION_POSITIVE | 5 | data/gaze.json | count(design.regions=0) |
| GAZE_REGION_NEGATIVE | 5 | data/gaze.json | count(design.regions=1) |
| GAZE_REGION_NEUTRAL | 3 | data/gaze.json | count(design.regions=2) |
| GAZE_WINDOWS | 3 | data/gaze.json | count(design.contexts[0].candidates) |
| GAZE_CONTRASTS | 58 | data/gaze.json | count(contrasts) |
| GAZE_TRANSFER_RECORDS | 40960 | data/gaze.json | count(transfer) |
| GAZE_TRANSFER_BRIDGES | 2 | data/gaze.json | count(unique(transfer.bridge)) |
| GAZE_TRANSFER_COMPARISON_COUNT | 4 | data/gaze.json | count(design.transfer_comparisons) |
| GAZE_TRANSFER_ENDPOINT_COUNT | 2 | data/gaze.json | count(unique(contrasts[experiment=transfer].endpoint)) |
| GAZE_ACTIVE_COMPARISON_COUNT | 7 | data/gaze.json | count(design.comparisons) |
| GAZE_ACTIVE_ENDPOINT_COUNT | 3 | data/gaze.json | count(unique(contrasts[experiment=active].endpoint)) |
| GAZE_TRANSFER_UNIFORMS | 127 | data/gaze.json | design.transfer_steps - initial location |
| GAZE_TRANSFER_CONTRASTS | 16 | data/gaze.json | count(contrasts[experiment=transfer]) |
| GAZE_ACTIVE_CONTRASTS | 42 | data/gaze.json | count(contrasts[experiment=active]) |
| BOUNDARY_UNITS | 9216 | data/boundary_gaze.json | count(unique(episodes.regime,scene,boundary,replicate)) |
| BOUNDARY_EPISODES | 55296 | data/boundary_gaze.json | count(episodes) |
| BOUNDARY_CONDITIONS | 6 | data/boundary_gaze.json | count(design.conditions) |
| BOUNDARY_CELLS | 18 | data/boundary_gaze.json | count(unique(episodes.regime,scene,boundary)) |
| BOUNDARY_SCENES | 3 | data/boundary_gaze.json | count(design.scene_maps) |
| BOUNDARY_STATES | 9 | data/boundary_gaze.json | count(design.scene_maps)^2 |
| BOUNDARY_REGIMES | 2 | data/boundary_gaze.json | count(design.regimes) |
| BOUNDARY_PROBES | 3 | data/boundary_gaze.json | count(design.probe_reliabilities) |
| BOUNDARY_CONTRASTS | 84 | data/boundary_gaze.json | count(region.intervals) |
| BOUNDARY_COMPARISONS | 7 | data/boundary_gaze.json | count(design.comparisons) |
| BOUNDARY_VISUAL_COMPARISONS | 5 | data/boundary_gaze.json | count(design.comparisons[reference=visual]) |
| BOUNDARY_ENDPOINT_COUNT | 2 | data/boundary_gaze.json | count(design.endpoints) |
| BOUNDARY_EXACT | 30 | data/boundary_gaze.json | count(exact_offsets) |
| JOINT_CONFIDENCE_PERCENT | 95 | data/gaze_uncertainty.json | 100 * design.confidence |
| JOINT_BLOCKS | 3 | data/gaze_uncertainty.json | count(region.blocks) |
| JOINT_MC_PERCENT | 99 | data/gaze_uncertainty.json | 100 * design.monte_carlo_confidence |
| POINTWISE_CONFIDENCE_PERCENT | 95 | data/statistical_calibration.json | 100 * (1 - alpha); declared analysis confidence level |
| POINTWISE_ALPHA | 0.05 | data/statistical_calibration.json | /alpha |
| POINTWISE_CONFIDENCE | 0.95 | data/statistical_calibration.json | 1 - alpha |
| POINTWISE_LOWER | 0.025 | data/statistical_calibration.json | alpha / 2 |
| POINTWISE_UPPER | 0.975 | data/statistical_calibration.json | 1 - alpha / 2 |
| EXACT_RETAINED_MASS | 0.666667 | data/exact_decision.json | /restricted_prior_mass |
| DISPLAY_SCALE | 1000 | data/statistics.json | display convention; estimates remain in native units |
| GNN_VERSION | 4.1.0 | data/provenance.json | dependencies[distribution=generalized-notation-notation].version |
| GNN_COMMIT | 46459949944e3217f8a6a804d4ff8c52829ef275 | data/provenance.json | dependencies[distribution=generalized-notation-notation].commit |
| RE_VERSION | 3.0.0 | data/provenance.json | dependencies[distribution=realizing-emptiness].version |
| RE_COMMIT | bd91fa1c230551180ed741d1951840e3628da35d | data/provenance.json | dependencies[distribution=realizing-emptiness].commit |
| PRACTICE_REVERSAL_SCHEDULE | 0.85 for 4 windows; 0.15 for 4 windows; 0.85 for 4 windows | data/emptiness_practice.json | /design/contexts[-1]/probabilities; run-length encoding |
| PRACTICE_STATIONARY_PROBABILITY | 0.85 | data/emptiness_practice.json | /design/contexts/0/probabilities/0 |
| BOUNDARY_MIDDLE_RELIABILITY | 0.8 | data/boundary_gaze.json | /design/probe_reliabilities[middle] |
| GAZE_STATIONARY_SEQUENCE | 0,0,0 | data/gaze.json | design.contexts[name=stationary].candidates |
| GAZE_REVERSAL_SEQUENCE | 0,2,0 | data/gaze.json | design.contexts[name=reversal].candidates |

These finite synthetic experiments and software gates do not establish human effects.
