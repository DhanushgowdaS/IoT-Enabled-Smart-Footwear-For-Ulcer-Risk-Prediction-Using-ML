# PROCEDURE

## Project
IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using ML

This file records project work using **What, When, Why, Where, How**.

---

## 2026-10-04 — Repository Reset for Client 2

### What
The GitHub repository was cleaned and rebuilt as the Client 2 working repository.

### When
2026-10-04

### Why
The previous repository contained Client 1/experimental ML, dataset, backend, and dashboard files. They are not the correct source for the new Client 2 healthy-baseline ML workflow.

### Where
GitHub:
`DhanushgowdaS/IoT-Enabled-Smart-Footwear-For-Ulcer-Risk-Prediction-Using-ML`

### How
1. Reviewed the existing repository.
2. Used the Client 1 ZIP only for required hardware reference files.
3. Removed the old Random Forest/risk-map workflow and old backend/dashboard files.
4. Added the Client 2 source dataset.
5. Added new Client 2 ML training/testing scripts.
6. Added updated hardware documentation.
7. Added this procedure file for future tracking.

---

## 2026-10-04 — Client 2 Dataset

### What
Added the new Client 2 footwear dataset containing Person A and Person B sensor data.

### When
2026-10-04

### Why
The new ML method must learn healthy pressure/temperature patterns instead of assigning risk labels from scenario names.

### Where
`Data/client2_footwear_dataset.csv`

### How
The dataset was checked for joined CSV records. The source contains malformed lines where two records were joined without a newline. The ML training script repairs those records in memory before filtering RAW records.

AVG10 records are excluded from model training because they are derived averages.

---

## 2026-10-04 — Healthy-Baseline ML

### What
Prepared an unsupervised Isolation Forest model workflow.

### When
2026-10-04

### Why
The Client 2 dataset provides healthy reference subjects but does not provide labelled ulcer/non-ulcer clinical outcomes. Isolation Forest can learn the healthy distribution without inventing ulcer labels.

### Where
- `ML/train_model_client2.py`
- `ML/test_model_client2.py`
- `ML/CLIENT2_ML_README.md`

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
