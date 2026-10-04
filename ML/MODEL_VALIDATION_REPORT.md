# ML Model Validation Report

## Final status

**PASSED** — the healthy-reference model was rebuilt to match the 10-second ESP32 input format and to use scenario context.

## Dataset

- Logical records after CSV repair: 6,103
- AVG10 records used for ML: 555
- RAW records excluded from model fitting: 5,548
- Healthy reference persons: Person A and Person B
- Scenarios: 9

## Training Input

The model now uses **AVG10 records only**. These records represent the 10-second averaged sensor windows used by the ESP32.

This removes the previous mismatch where the model was fitted on RAW readings while the live device sent averaged readings.

## Scenario Awareness

Scenario is included as one-hot encoded model features.

Therefore a live reading marked Walking is evaluated in the context of the healthy Walking patterns in the reference dataset.

## 80 / 10 / 10 Split

The AVG10 records are split chronologically inside each Person + Scenario group:

| Split | Rows |
|---|---:|
| Training | 444 |
| Validation | 55 |
| Testing | 56 |

## Model

- StandardScaler
- IsolationForest
- 500 trees
- Random state: 42
- 13 numeric features
- 9 one-hot scenario features

## Validation Thresholds

| Threshold | Value |
|---|---:|
| q50 | -0.0005867 |
| q90 | 0.0273910 |
| q95 | 0.0383011 |
| q98 | 0.0395712 |
| q99 | 0.0513628 |

## Held-Out Healthy Test

All 56 held-out AVG10 healthy records were classified as **Safe** under the displayed mismatch-risk rule:

| Risk indication | Count |
|---|---:|
| Safe | 56 |
| Low Risk | 0 |
| Medium Risk | 0 |
| High Risk | 0 |

The 60 healthy AVG10 Walking reference records also produced:

| Walking risk indication | Count |
|---|---:|
| Safe | 60 |
| Low Risk | 0 |
| Medium Risk | 0 |
| High Risk | 0 |

This is a healthy-reference stability check, not clinical validation.

## Important Limitation

The supplied dataset contains healthy reference data only. The system therefore provides a **healthy-pattern deviation / ulcer-risk indication** and does not establish clinical ulcer probability, diagnostic accuracy, sensitivity, or specificity.

Mismatch % is not ulcer probability.
