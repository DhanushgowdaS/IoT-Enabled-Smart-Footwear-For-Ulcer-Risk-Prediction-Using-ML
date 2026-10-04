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
| GPIO36 | FSR2 |
| GPIO32 | FSR3 |
| GPIO33 | FSR4 |
| GPIO4 | DS18B20 DATA |

## Project Structure

```text
Hardware/
Firmware/
Data/footwear_dataset.csv
ML/train_model.py
ML/test_model.py
ML/ML_README.md
PROCEDURE.md
requirements.txt
README.md
```

## ML Model Artifact

The binary model file `ML/ulcer_risk_model.pkl` is generated locally by `ML/train_model.py`.

## Current Status

Source dataset, firmware sensor tests, hardware documentation, and healthy-baseline ML workflow are prepared. FastAPI and Streamlit integration will be added after ML validation.
