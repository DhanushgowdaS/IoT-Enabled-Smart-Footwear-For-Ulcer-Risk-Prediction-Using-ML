# PROCEDURE

## Project
IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using ML

This file records project work using What, When, Why, Where, How.

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

---

## 2026-10-04 — FastAPI and ESP32 Integration

### What
Connected the ESP32 firmware to the deployed FastAPI backend.

### Where
- `Firmware/Microcontrolle_ESP32_new_code.ino`
- `main.py`
- Render service

### How
1. ESP32 reads four FSR sensors and one DS18B20.
2. Sensor values are averaged over 5-second windows.
3. ESP32 sends the JSON payload to the Render `/log` endpoint over HTTPS.
4. FastAPI runs the saved healthy-baseline ML model.
5. The result is stored in SQLite and CSV.
6. `/latest` and `/data` provide readings to the dashboard.
7. Automatic HTTPS retries were added to tolerate temporary connection failures.

### Result
Live ESP32 requests returned HTTP 200 with ML outputs during testing.

---

## 2026-10-04 — Streamlit Dashboard Integration

### What
Integrated the live Streamlit dashboard with the deployed API.

### Where
`app.py`

### How
1. Dashboard reads `/latest` and `/data`.
2. Requests use no-cache headers and cache-busting parameters.
3. Dashboard refreshes every 5 seconds.
4. Backend timestamps are displayed in IST.
5. Pressure, temperature, 10-minute risk counts and the latest 20 readings are displayed.
6. CSV download uses the deployed API.

### Result
The dashboard is configured to consume the current Render API instead of the earlier local/legacy backend.

---

## Future Updates

For every significant change, add a new dated section:

- **What** — what changed
- **When** — date/time
- **Why** — reason
- **Where** — affected files/location
- **How** — implementation and validation steps

### Important limitation

The supplied dataset contains healthy reference data only. The system therefore provides a healthy-pattern deviation/risk indication and is not clinically validated.
