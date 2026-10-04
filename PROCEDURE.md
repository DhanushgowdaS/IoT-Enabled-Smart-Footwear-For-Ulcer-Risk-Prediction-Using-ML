# PROCEDURE

## Project
IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using ML

## 2026-10-04 — Live ML Alignment

### What
Rebuilt the ML pipeline to match the sensor-processing method used during data collection and the current ESP32 firmware.

### When
2026-10-04

### Why
The ESP32 was changed back to a 10-second averaging window because the healthy reference dataset contains AVG10 records. The previous model was trained on RAW records, creating a mismatch between training input and live input.

### Where
- Firmware/Microcontrolle_ESP32_new_code.ino
- ML/train_model.py
- ML/predict.py
- ML/test_model.py
- ML/random_test.py
- main.py
- ML/model_validation_report.json
- ML/MODEL_VALIDATION_REPORT.md

### How
1. ESP32 averages sensor readings over 10 seconds.
2. ML training now uses AVG10 records only.
3. Scenario is passed from the ESP32 into the ML input.
4. Scenario is one-hot encoded so activity context is part of the healthy baseline.
5. The model is retrained using StandardScaler + IsolationForest.
6. Validation thresholds are recalibrated from the new validation set.
7. Healthy AVG10 test records are checked through the same inference path.
8. The FastAPI backend passes the scenario into the model.

### Result
The rebuilt model classified all 60 healthy AVG10 Walking reference records as Safe during the local validation check.

### Limitation
The supplied dataset contains healthy reference data only. The output is a project-level healthy-pattern deviation/risk indication and is not a clinical diagnosis.
