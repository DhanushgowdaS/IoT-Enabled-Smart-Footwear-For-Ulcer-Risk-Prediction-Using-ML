# Machine Learning Model

## Concept

The model learns the pressure and temperature patterns of healthy reference users and measures how much a new footwear reading deviates from that healthy pattern.

\`\`\`
Healthy reference data
Person A + Person B
        ↓
80% Training
        ↓
Isolation Forest
        ↓
Healthy baseline
        ↑
10% Validation → q95 / q98 / q99 thresholds
        ↑
10% Test → final held-out healthy stability check

New sensor reading
FSR1 FSR2 FSR3 FSR4 + Temperature
        ↓
Same feature engineering + scaling
        ↓
Anomaly score
        ↓
Healthy-pattern mismatch %
        ↓
Safe / Low Risk / Medium Risk / High Risk
\`\`\`

## Data handling

- RAW records are used for model training and evaluation.
- AVG10 records are excluded because they are derived averages.
- Concatenated CSV records are repaired before parsing.
- Split is chronological inside each Person + Scenario group to reduce direct temporal leakage.

## Features

- FSR1, FSR2, FSR3, FSR4
- Temperature
- FSR average
- FSR maximum and minimum
- FSR standard deviation
- FSR distribution ratios

## Model

\`StandardScaler\` followed by \`IsolationForest\` with 500 trees.

The model is unsupervised: it does not learn an \`ulcer / no-ulcer\` class because the supplied dataset does not contain true ulcer labels.

## Prediction

A higher anomaly score means the current reading is less similar to the healthy reference pattern.

\`\`\`
Mismatch = clip((AnomalyScore - q95) / (q99 - q95) × 100, 0, 100)
Healthy Match = 100 - Mismatch
\`\`\`

| Condition | Risk indication |
|---|---|
| score ≤ q95 | Safe |
| q95 < score ≤ q98 | Low Risk |
| q98 < score ≤ q99 | Medium Risk |
| score > q99 | High Risk |

The q95/q98/q99 thresholds are calibrated from the validation split only.

## Important limitation

Mismatch % is a project-specific healthy-pattern deviation index. It is not ulcer probability. Because the supplied dataset contains healthy reference data only, clinical accuracy, sensitivity, specificity, and diagnostic performance cannot be claimed yet.

## Files

- \`train_model.py\` — trains and saves the model
- \`predict.py\` — reusable inference function for FastAPI/Streamlit
- \`test_model.py\` — full inference and sanity tests
- \`ulcer_risk_model.pkl\` — generated model artifact
- \`model_validation_report.json\` — training/validation/test report
- \`test_results.json\` — final inference test output
