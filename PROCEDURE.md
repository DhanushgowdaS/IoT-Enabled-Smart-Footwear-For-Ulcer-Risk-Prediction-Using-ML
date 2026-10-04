# PROCEDURE

## Project
IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using ML

This file records project work using **What, When, Why, Where, How**.

---

## 2026-10-04 — Repository Reset

### What
The GitHub repository was cleaned and rebuilt as the working repository for the current project development.

### When
2026-10-04

### Why
The previous repository contained experimental ML, dataset, backend, and dashboard files that did not match the current healthy-baseline ML workflow.

### Where
GitHub:
`DhanushgowdaS/IoT-Enabled-Smart-Footwear-For-Ulcer-Risk-Prediction-Using-ML`

### How
1. Reviewed the existing repository.
2. Used the earlier project archive only for required hardware and firmware reference files.
3. Removed the old Random Forest/risk-map workflow and old backend/dashboard files.
4. Added the current footwear dataset.
5. Added the new healthy-baseline ML training/testing scripts.
6. Added updated hardware documentation.
7. Added this procedure file for future tracking.

---

## 2026-10-04 — Dataset

### What
Added the footwear dataset containing Person A and Person B sensor data.

### When
2026-10-04

### Why
The ML method learns healthy pressure/temperature patterns instead of assigning risk labels from scenario names.

### Where
`Data/footwear_dataset.csv`

### How
The source data was checked for joined CSV records. The ML training script repairs joined records in memory before filtering RAW records. AVG10 records are excluded from model training because they are derived averages.

---

## 2026-10-04 — Healthy-Baseline ML Workflow

### What
Prepared an unsupervised Isolation Forest model workflow.

### When
2026-10-04

### Why
The dataset provides healthy reference subjects but does not provide labelled ulcer/non-ulcer clinical outcomes. Isolation Forest can learn the healthy distribution without inventing ulcer labels.

### Where
- `ML/train_model.py`
- `ML/test_model.py`
- `ML/ML_README.md`

### How
1. Repair joined CSV records in memory.
2. Keep RAW records only.
3. Build FSR, temperature, pressure-summary, and FSR-ratio features.
4. Standardize the features.
5. Train Isolation Forest using healthy Person A + Person B data.
6. Calculate anomaly score as the negative Isolation Forest decision function.
7. Calibrate the healthy score distribution.
8. Convert deviation to a project-specific mismatch percentage.
9. Map mismatch to the four project risk-indication bands.

The generated model artifact is created locally as `ML/ulcer_risk_model.pkl` when the training script is run.

---

## Future Updates

For every significant change, add a new dated section:

- **What** — what changed
- **When** — date/time
- **Why** — reason
- **Where** — affected files/location
- **How** — implementation and validation steps

Planned next stages:
1. Validate model by person and scenario.
2. Test artificial abnormal sensor patterns.
3. Integrate model into FastAPI.
4. Add real-time mismatch and risk columns.
5. Replace old majority-count logic with rolling 5-minute assessment.
6. Update ESP32 API firmware.
7. Update Streamlit dashboard.
8. Test and deploy.


---

## 2026-10-04 — ML Training, Validation and Testing

### What
Built and validated the new healthy-baseline ML model.

### When
2026-10-04

### Why
To use the supplied healthy reference data to learn normal pressure/temperature patterns and measure deviation for ulcer-risk indication without inventing clinical labels.

### Where
- `ML/train_model.py`
- `ML/predict.py`
- `ML/test_model.py`
- `ML/ML_README.md`
- `ML/MODEL_VALIDATION_REPORT.md`
- `ML/model_validation_report.json`
- `ML/test_results.json`

### How
1. Repaired the six joined CSV lines in memory.
2. Obtained 6,103 logical records.
3. Used 5,548 RAW records and excluded 555 AVG10 records.
4. Split RAW data into 4,438 training, 555 validation and 555 test records.
5. Fit StandardScaler on training data only.
6. Trained a 500-tree Isolation Forest on healthy Person A + Person B data.
7. Calibrated q95, q98 and q99 thresholds from validation data only.
8. Tested all 5,548 RAW records through the saved model.
9. Tested a deterministic random real dataset line.
10. Tested additional synthetic sensor patterns for inference stability and valid output ranges.

### Result
All software/model pipeline tests passed. The held-out healthy test produced 3.60% above q95, 1.08% above q98 and 0.90% above q99.

Because the supplied data contains healthy reference records only, these results are stability/false-alert measurements, not ulcer classification accuracy.
