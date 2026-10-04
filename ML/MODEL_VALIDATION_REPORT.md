# ML Model Validation Report

## Final status

**PASSED** — training, validation, held-out testing, full-dataset inference, random-row inference, and synthetic-data pipeline tests completed without errors.

## Dataset used

The supplied footwear dataset was repaired before parsing. Six physical CSV lines contained two concatenated records.

- Logical records: 6,103
- RAW records used by ML: 5,548
- AVG10 records excluded: 555
- Healthy persons: Person A and Person B

## 80 / 10 / 10 split

The 5,548 RAW records were divided chronologically inside each Person + Scenario group:

| Split | Rows | Share |
|---|---:|---:|
| Training | 4,438 | 79.99% |
| Validation | 555 | 10.00% |
| Testing | 555 | 10.00% |

Training fits the scaler and Isolation Forest. Validation is used only to calibrate q95/q98/q99. The final test split remains untouched until evaluation.

## Model

- StandardScaler
- IsolationForest
- 500 trees
- Fixed random state: 42
- 13 engineered features

## Held-out healthy test

The test set contains healthy reference records, so the useful measurement is healthy false-alert/stability rate at the selected anomaly thresholds, not classification accuracy.

The generated JSON report contains the exact thresholds and held-out rates.

## Random real-dataset test

A deterministic random RAW line from the new dataset was passed through the saved model after training. The exact row and prediction are stored in \`test_results.json\`.

## Synthetic tests

Additional synthetic sensor patterns were passed through the inference pipeline to verify finite scores, bounded mismatch values, and valid risk labels.

These synthetic tests are software/pipeline tests, not clinical validation.

## What the model predicts

The model does not predict \`ulcer = yes/no\` from a labeled dataset. It predicts how unusual the current pressure-temperature pattern is compared with the healthy reference pattern.

The next real-time layer can combine repeated readings over a 5-minute window to look for sustained deviation before producing the overall project-level ulcer-risk indication.
