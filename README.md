# IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using ML

An ESP32-based smart footwear system that monitors four FSR pressure sensors and a DS18B20 temperature sensor for diabetic foot-ulcer risk indication.

## Client 2 ML Approach

Client 2 uses healthy-reference data from Person A and Person B to learn normal pressure/temperature patterns.

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
Data/client2_footwear_dataset.csv
ML/train_model_client2.py
ML/test_model_client2.py
ML/CLIENT2_ML_README.md
PROCEDURE.md
requirements.txt
README.md
```

## ML Model Artifact

The binary model file `ML/ulcer_risk_model.pkl` is generated locally by `ML/train_model_client2.py`. The repository currently keeps the reproducible training workflow rather than the generated binary artifact.

## Current Status

Repository reset for Client 2. Source dataset, firmware sensor tests, hardware documentation, and healthy-baseline ML workflow are prepared. FastAPI and Streamlit integration will be added after ML validation.
