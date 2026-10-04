# Machine Learning Model

## Concept

The model learns healthy pressure and temperature patterns using the same **10-second averaged format** sent by the ESP32.

Healthy reference data from Person A and Person B is represented by AVG10 records. Scenario is included as a one-hot feature so a Walking reading is evaluated in the context of healthy Walking patterns.

```text
Healthy reference AVG10 data
Person A + Person B
        ↓
80% Training
        ↓
Scenario-aware Isolation Forest
        ↑
10% Validation → q95 / q98 / q99
        ↑
10% Test

ESP32
10-second sensor average
        ↓
Same feature engineering + scenario
        ↓
Anomaly score
        ↓
Healthy-pattern mismatch %
        ↓
Safe / Low Risk / Medium Risk / High Risk
```

## Data handling

- AVG10 records are used for model training and evaluation.
- RAW records are excluded from model fitting.
- AVG10 represents the same 10-second averaging window used by the ESP32.
- Concatenated CSV records are repaired before parsing.
- Split is chronological inside each Person + Scenario group.

## Features

Numeric:
- FSR1, FSR2, FSR3, FSR4
- Temperature
- FSR average
- FSR maximum and minimum
- FSR standard deviation
- FSR distribution ratios

Scenario:
- One-hot encoding of the dataset scenarios.

## Model

`StandardScaler` followed by `IsolationForest` with 500 trees.

The model is unsupervised: the supplied dataset contains healthy reference data only and does not contain clinical ulcer/no-ulcer labels.

## Prediction

A higher anomaly score means the current reading is less similar to the healthy reference distribution for its scenario.

```
Mismatch =
clip((AnomalyScore - q95) / (q99 - q95) × 100, 0, 100)

Healthy Match = 100 - Mismatch
```

| Displayed mismatch | Risk indication |
|---|---|
| 0–10% | Safe |
| >10–33.33% | Low Risk |
| >33.33–66.67% | Medium Risk |
| >66.67–100% | High Risk |

Mismatch % is a project-specific healthy-pattern deviation index, not ulcer probability.

## Important limitation

Because the dataset contains healthy reference data only, clinical accuracy, sensitivity, specificity, and diagnostic performance cannot be claimed.

## Files

- `train_model.py` — trains and saves the scenario-aware AVG10 model
- `predict.py` — reusable inference function for FastAPI
- `test_model.py` — AVG10 model tests
- `random_test.py` — random Walking input test
- `ulcer_risk_model.pkl` — generated model artifact
- `model_validation_report.json` — validation report
- `test_results.json` — model test results
