# IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using ML

An ESP32-based smart footwear system that monitors four FSR pressure sensors and a DS18B20 temperature sensor for diabetic foot-ulcer risk indication.

## ML Approach

The system uses healthy-reference data from Person A and Person B to learn normal pressure/temperature patterns.

- Isolation Forest anomaly detection
- StandardScaler preprocessing
- Pressure-distribution feature engineering
- Healthy-pattern mismatch percentage
- Safe / Low Risk / Medium Risk / High Risk indication

Mismatch % is a project-specific deviation index from the healthy reference pattern. It is **not ulcer probability** and the system is not a clinical diagnostic device.

## Hardware

- ESP32
- 4 × FSR sensors
- DS18B20 temperature sensor
- 4 × 10 kΩ resistors
- 4.7 kΩ pull-up resistor

## Pin Configuration

| ESP32 | Component |
|---|---|
| GPIO34 | FSR1 |
| GPIO35 | FSR2 |
| GPIO32 | FSR3 |
| GPIO33 | FSR4 |
| GPIO4 | DS18B20 DATA |

## Project Structure

```text
Hardware/
Firmware/
Data/footwear_dataset.csv
ML/
├── train_model.py
├── predict.py
├── test_model.py
├── ML_README.md
├── MODEL_VALIDATION_REPORT.md
├── model_validation_report.json
└── test_results.json
main.py
app.py
render.yaml
requirements.txt
README.md
PROCEDURE.md
```

## Backend and Dashboard

- `main.py` — FastAPI backend, ML inference and data storage
- `app.py` — Streamlit real-time dashboard
- `render.yaml` — Render configuration for the API
- `ML/predict.py` — reusable model inference

## Live Integration

ESP32 sends averaged sensor readings to the deployed FastAPI backend over HTTPS every 5 seconds. The backend runs the saved healthy-baseline ML model and stores the resulting reading. The Streamlit dashboard reads the latest and recent records from the same backend.

## Current Status

The healthy-baseline ML workflow, ESP32 firmware, FastAPI backend, cloud API integration and Streamlit dashboard are prepared for live testing.
