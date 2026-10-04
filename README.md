# IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using Machine Learning

An IoT-enabled smart footwear prototype that monitors multi-point foot pressure and temperature, sends the readings to an online backend, analyzes the incoming pattern against healthy reference data, and presents a real-time ulcer-risk indication through a Streamlit dashboard.

> **Important:** This is an engineering/research prototype for monitoring and early risk indication. It is **not a clinically validated medical diagnostic device**. The displayed mismatch percentage is a project-specific deviation from the learned healthy pattern; it is not ulcer probability.

## 1. Project Overview

The project combines:

- Embedded sensing using an ESP32
- Four Force Sensitive Resistor (FSR) pressure sensors
- One DS18B20 digital temperature sensor
- Wi-Fi/HTTPS communication
- FastAPI backend
- SQLite/CSV local storage on the backend
- Healthy-pattern Machine Learning using Isolation Forest
- Streamlit real-time dashboard
- GitHub source control
- Render deployment for the backend

The final implemented prototype differs slightly from the earlier concept documents. The earlier design documents described a larger sensing arrangement, while the implemented prototype uses **4 FSRs + 1 DS18B20**, matching the current firmware and backend.

## 2. Problem Statement

Foot-ulcer risk monitoring can benefit from observing pressure distribution and temperature changes over time. A conventional insole does not continuously collect these measurements or send them to a connected monitoring system.

This project demonstrates a low-cost connected footwear prototype that:

1. Measures pressure at multiple foot regions.
2. Measures foot temperature.
3. Collects and averages sensor readings on the ESP32.
4. Sends measurements to an online backend.
5. Compares the current pattern with healthy reference data.
6. Calculates a healthy-pattern mismatch value.
7. Displays the latest readings, trends and risk indication through a dashboard.

## 3. Main Objectives

- Build a smart insole using multiple pressure sensing points.
- Monitor foot temperature together with pressure.
- Process sensor readings using an ESP32.
- Send data over Wi-Fi and HTTPS.
- Store time-stamped readings.
- Build a structured dataset for Machine Learning.
- Train a healthy-reference anomaly model.
- Convert anomaly score into a project-level mismatch percentage.
- Generate Safe, Low Risk, Medium Risk and High Risk indications.
- Show live pressure and temperature trends.
- Provide a recent 5-minute overall risk assessment.
- Maintain a reproducible firmware, backend, ML and dashboard workflow.

## 4. Final System Architecture

```text
                 SMART FOOTWEAR / INSOLE
                           |
            +--------------+--------------+
            |                             |
       4 × FSR Sensors             DS18B20 Sensor
            |                             |
            +--------------+--------------+
                           |
                         ESP32
                           |
                 10 × 1-second samples
                           |
                  10-second average
                           |
                       HTTPS/JSON
                           |
                           v
               FastAPI Backend on Render
                           |
              +------------+------------+
              |                         |
        SQLite + CSV               ML Inference
              |                         |
              |              Healthy-reference model
              |                    (Isolation Forest)
              |                         |
              |               Anomaly → Mismatch
              |                         |
              +------------+------------+
                           |
                           v
                 Streamlit Dashboard
                           |
          +----------------+----------------+
          |                                 |
   Live sensor charts                Risk indication
   Latest 20 records                 5-minute assessment
```

## 5. Hardware

### 5.1 Final Implemented Components

| Component | Quantity | Purpose |
|---|---:|---|
| ESP32 development board | 1 | Main controller, ADC acquisition and Wi-Fi |
| FSR pressure sensor | 4 | Measures relative pressure at four insole locations |
| DS18B20 digital temperature sensor | 1 | Measures foot temperature |
| 10 kΩ resistor | 4 | FSR voltage-divider resistors |
| 4.7 kΩ resistor | 1 | DS18B20 DATA-line pull-up |
| Battery / regulated power supply | 1 | Powers the prototype |
| On/off switch | 1 | Power control |
| Wires/connectors | As required | Electrical interconnection |
| Insole/base | 1 | Mechanical support and sensor placement |

### 5.2 Final Pin Configuration

| ESP32 GPIO | Connected Device |
|---|---|
| GPIO34 | FSR1 |
| GPIO35 | FSR2 |
| GPIO32 | FSR3 |
| GPIO33 | FSR4 |
| GPIO4 | DS18B20 DATA |

### 5.3 FSR Interface

Each FSR is used in a voltage-divider arrangement with a 10 kΩ resistor. As pressure changes, the FSR resistance changes and the divider output changes. The ESP32 reads the corresponding analog value.

The firmware uses the ESP32 ADC reading range directly for the ML pipeline.

### 5.4 DS18B20 Interface

The DS18B20 is connected using the OneWire interface. A 4.7 kΩ pull-up resistor is used on the DATA line.

The final firmware reads one DS18B20 device at GPIO4.

## 6. Sensor Placement

The four FSRs are distributed across the insole so that different pressure regions can be observed. The exact mechanical position depends on the physical insole construction.

A practical arrangement is:

```text
             TOE / FOREFOOT
          +-----------------+
          |   FSR3   FSR4   |
          |                 |
          |      FSR2       |
          |                 |
          |      FSR1       |
          +-----------------+
                 HEEL
```

The diagram represents the sensing concept only. Final physical placement should follow the actual fabricated insole.

## 7. Embedded/Firmware Workflow

The final ESP32 firmware is in:

`Firmware/Microcontrolle_ESP32_new_code.ino`

The firmware performs the following sequence:

1. Start Serial Monitor at 115200 baud.
2. Initialize the DS18B20 sensor.
3. Connect the ESP32 to Wi-Fi.
4. Maintain automatic Wi-Fi reconnection.
5. Take one sensor sample at approximately one-second intervals.
6. Read FSR1–FSR4.
7. Request and read the DS18B20 temperature.
8. Continue until 10 valid temperature/sensor samples are collected.
9. Average the 10 one-second samples.
10. Send the resulting 10-second average to the backend.
11. Wait for the next 10-second collection window.
12. Retry the HTTPS POST up to five times if transmission fails.

### 7.1 Important Timing Alignment

The current ML model is trained on **AVG10** data. Therefore the live firmware also creates one record from exactly **10 one-second samples**, representing a 10-second averaging window.

This alignment is important because training data and live inference data must use the same measurement format.

### 7.2 JSON Sent by ESP32

The current firmware sends:

```json
{
  "scenario": "Walking",
  "fsr1": 0,
  "fsr2": 0,
  "fsr3": 0,
  "fsr4": 0,
  "temp1": 0
}
```

The current firmware uses `Walking` as the scenario value.

## 8. Firmware Libraries

The final firmware uses:

- WiFi
- WiFiClientSecure
- HTTPClient
- ArduinoJson
- OneWire
- DallasTemperature

These are used for Wi-Fi, HTTPS, JSON serialization and temperature sensing.

## 9. Dataset

The repository contains:

`Data/footwear_dataset.csv`

The supplied dataset contains healthy-reference measurements from:

- Person A
- Person B

The dataset contains multiple scenarios, including:

- Standing
- Sitting
- Walking
- No_Load
- Toe_Pressure
- Heel_Pressure
- High_Pressure
- Right_Shift
- Left_Shift

The source CSV contains both:

- `RAW` records
- `AVG10` records

The training pipeline repairs six physically joined CSV lines in memory before parsing.

### Current dataset summary

| Item | Value |
|---|---:|
| Physical CSV lines including header | 6,098 |
| Logical records after repair | 6,103 |
| RAW records | 5,548 |
| AVG10 records | 555 |
| Healthy reference persons | 2 |
| Scenarios represented | 9 |

The ML workflow uses the **555 AVG10 records** and excludes the RAW records from model fitting.

## 10. Machine Learning Approach

### 10.1 Why the final model is not Random Forest

The earlier project concept described Random Forest supervised classification. During final implementation, the available dataset was found to contain healthy reference data rather than clinically labelled ulcer/non-ulcer outcomes.

Therefore, the final project uses:

**StandardScaler + Isolation Forest**

Isolation Forest is used to learn the structure of healthy observations and identify readings that deviate from that healthy pattern.

This is a better fit for the data actually available than inventing clinical class labels.

### 10.2 Final ML Flow

```text
Healthy AVG10 Data
Person A + Person B
          |
          v
Chronological 80 / 10 / 10 split
          |
    +-----+-----+
    |     |     |
   80%   10%   10%
 Training Validation Testing
    |       |
    |     Threshold
    |     calibration
    v
StandardScaler
    |
    v
Isolation Forest
500 trees
    |
    v
Anomaly Score
    |
    v
Mismatch %
    |
    v
Healthy Match %
    |
    v
Risk Indication
```

### 10.3 Features

The model uses 13 numeric features:

**Raw inputs**

- FSR1
- FSR2
- FSR3
- FSR4
- Temperature

**Pressure summary**

- FSR Average
- FSR Maximum
- FSR Minimum
- FSR Standard Deviation

**Pressure distribution**

- FSR1 Ratio
- FSR2 Ratio
- FSR3 Ratio
- FSR4 Ratio

The model also adds one-hot encoded **Scenario** features.

This means a live Walking reading is evaluated with the context of healthy Walking data rather than being treated the same as every other activity.

### 10.4 Model Configuration

- Preprocessing: StandardScaler
- Model: IsolationForest
- Trees: 500
- Contamination: auto
- Random state: 42
- Scenario encoding: one-hot
- Training input: AVG10 only
- Training window: 10 seconds

## 11. Mismatch and Risk Calculation

The model first produces an anomaly score.

The validation data is used to calculate percentile thresholds:

- q95
- q98
- q99

The project mismatch calculation is:

```text
Mismatch %
= clip(
    (Anomaly Score - q95)
    / (q99 - q95)
    × 100,
    0,
    100
)
```

Healthy match is:

```text
Healthy Match %
= 100 - Mismatch %
```

### 11.1 Risk Bands

| Mismatch | Displayed Indication |
|---:|---|
| 0–10% | Safe |
| >10–33.33% | Low Risk |
| >33.33–66.67% | Medium Risk |
| >66.67–100% | High Risk |

These are **project-defined risk indication bands**, not clinically validated medical thresholds.

### 11.2 Meaning of Mismatch

Mismatch percentage represents:

> How far the current sensor pattern deviates from the healthy reference pattern learned by the system.

It does **not** mean:

> Probability that the user has an ulcer.

## 12. Backend

The FastAPI backend is:

`main.py`

### Backend responsibilities

- Receive sensor data from the ESP32.
- Validate the incoming JSON fields.
- Prepare the ML input.
- Run the saved ML model.
- Calculate average and maximum pressure.
- Add a timestamp.
- Store the result in SQLite.
- Append the result to CSV.
- Maintain the latest reading in memory.
- Provide API endpoints for the dashboard.
- Provide CSV download.

### API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | API health check |
| `/log` | POST | Receive and process ESP32 readings |
| `/latest` | GET | Return latest reading |
| `/data` | GET | Return recent stored readings |
| `/download_csv` | GET | Download stored data as CSV |

### Backend data fields

Each processed record contains:

- timestamp
- scenario
- fsr1
- fsr2
- fsr3
- fsr4
- temp1
- avg_pressure
- max_pressure
- anomaly_score
- healthy_match_percent
- mismatch_percent
- ulcer_risk

### Online Backend

The current backend deployment is:

`https://iot-enabled-smart-footwear-for-ulcer.onrender.com`

The firmware posts to:

`https://iot-enabled-smart-footwear-for-ulcer.onrender.com/log`

## 13. Dashboard

The Streamlit dashboard is:

`app.py`

### Dashboard functions

- Live refresh every 5 seconds
- Current date/time display in IST
- Pressure analysis graph
- Temperature graph
- Overall Risk Assessment
- Recent 5-minute reading window
- Latest 20 readings table
- Risk status indicators
- CSV download

### 13.1 Pressure Analysis

The pressure graph displays FSR1–FSR4 over the recent time window.

### 13.2 Temperature

The temperature graph shows the DS18B20 temperature trend.

### 13.3 Overall Risk Assessment

The dashboard evaluates the latest **5-minute window** and displays:

- Overall risk indication
- Number of readings in the last 5 minutes
- Latest mismatch percentage

### 13.4 Latest Entries

The dashboard displays the latest 20 records containing:

- Timestamp
- Status
- FSR1
- FSR2
- FSR3
- FSR4
- Temperature

## 14. ML and Project Files

```text
.
├── .devcontainer/
│   └── devcontainer.json
├── Data/
│   └── footwear_dataset.csv
├── Firmware/
│   ├── DS18B20_testing_code.ino
│   ├── FSR_testing_code.ino
│   ├── Microcontrolle_ESP32_new_code.ino
│   └── Microcontrolle_ESP32_old_code.ino
├── Hardware/
│   ├── Circuit.md
│   └── Components.md
├── ML/
│   ├── ML_README.md
│   ├── MODEL_VALIDATION_REPORT.md
│   ├── model_validation_report.json
│   ├── predict.py
│   ├── random_test.py
│   ├── test_model.py
│   └── train_model.py
├── app.py
├── main.py
├── PROCEDURE.md
├── README.md
├── render.yaml
└── requirements.txt
```

## 15. Important ML Files

### `ML/train_model.py`

- Repairs the CSV format in memory.
- Loads the dataset.
- Filters AVG10 rows.
- Creates scenario-aware features.
- Performs the 80/10/10 split.
- Fits StandardScaler.
- Trains Isolation Forest.
- Calibrates validation thresholds.
- Saves the trained model artifact.
- Generates a machine-readable validation report.

### `ML/predict.py`

- Loads the saved model.
- Recreates the same features used during training.
- Requires a known Scenario.
- Produces:
  - Anomaly Score
  - Healthy Match %
  - Mismatch %
  - Ulcer Risk

### `ML/test_model.py`

Checks that:

- The model artifact is complete.
- AVG10 records can be passed through inference.
- Scores are finite.
- Mismatch remains between 0 and 100.
- Only valid risk labels are produced.

### `ML/random_test.py`

Runs a reproducible synthetic input test using the current prediction function.

## 16. Local Setup

### Python environment

Install the required packages:

```bash
pip install -r requirements.txt
```

### Train the model

The model must exist before importing the backend prediction module:

```bash
python ML/train_model.py
```

### Test the model

```bash
python ML/test_model.py
```

### Start FastAPI

```bash
uvicorn main:app --reload
```

### Start Streamlit

In another terminal:

```bash
streamlit run app.py
```

## 17. ESP32 Setup

1. Install Arduino IDE.
2. Install the ESP32 board package.
3. Install the required libraries.
4. Connect the FSR voltage-divider outputs to GPIO34, GPIO35, GPIO32 and GPIO33.
5. Connect DS18B20 DATA to GPIO4.
6. Confirm the 4.7 kΩ DS18B20 pull-up.
7. Update the Wi-Fi SSID and password in the firmware.
8. Confirm the Render backend URL.
9. Select the correct ESP32 board and COM port.
10. Upload `Firmware/Microcontrolle_ESP32_new_code.ino`.
11. Open Serial Monitor at 115200 baud.
12. Confirm Wi-Fi connection, sensor readings and HTTP response.

## 18. Firmware Testing Sequence

Before using the complete firmware, the repository contains simple testing sketches.

### FSR testing

Use:

`Firmware/FSR_testing_code.ino`

Purpose:

- Verify each ADC channel.
- Confirm FSR readings change when pressure is applied.
- Detect wiring problems before ML testing.

### Temperature testing

Use:

`Firmware/DS18B20_testing_code.ino`

Purpose:

- Confirm the DS18B20 is detected.
- Confirm temperature values are reasonable.
- Verify GPIO4 and the pull-up arrangement.

Only after these individual tests should the main firmware be uploaded.

## 19. Complete End-to-End Flow

```text
1. User wears / interacts with the smart footwear
                 |
2. FSR1–FSR4 + DS18B20 collect sensor data
                 |
3. ESP32 takes 10 samples at 1-second intervals
                 |
4. ESP32 calculates a 10-second average
                 |
5. ESP32 sends JSON over HTTPS
                 |
6. FastAPI receives the record
                 |
7. ML feature engineering is performed
                 |
8. Scenario-aware Isolation Forest inference
                 |
9. Anomaly score is converted to mismatch %
                 |
10. Healthy match and risk indication are generated
                 |
11. Result is stored in SQLite/CSV
                 |
12. Streamlit retrieves the data
                 |
13. Dashboard shows live charts and status
                 |
14. Recent 5-minute data contributes to the overall indication
```

## 20. Demonstration Testing

The prototype can be demonstrated using controlled pressure changes.

### Normal demonstration

- Keep pressure distributed naturally.
- Walk normally on the footwear.
- Observe the pressure curves and mismatch percentage.
- The healthy Walking reference should produce predominantly normal/low-deviation results when the sensor pattern is similar to the reference data.

### Abnormal demonstration

A simple demonstration method is to apply strong, localized or highly imbalanced pressure with a hand over one sensor region while keeping the other regions comparatively unloaded.

Example:

```text
FSR1  → strong pressure
FSR2  → low pressure
FSR3  → low pressure
FSR4  → low pressure
```

Hold the pressure long enough for a complete 10-second averaged reading to be generated.

The purpose of this test is to create a sensor pattern that is substantially different from the healthy reference pattern.

> A demonstration result is not clinical evidence. A high project risk indication only means the observed pattern deviated strongly from the learned healthy reference.

## 21. Deployment

Render is used for the FastAPI backend.

The deployment configuration is in:

`render.yaml`

The current build process installs dependencies and retrains the ML model:

```text
pip install -r requirements.txt
        +
python ML/train_model.py
```

The API starts with Uvicorn.

The build filter is configured so changes to the backend, ML files, dataset, dependencies or Render configuration can trigger a backend deployment, while unrelated firmware/dashboard-only changes do not need to rebuild the API.

## 22. Storage Note

The current backend stores data locally in:

- SQLite database
- CSV file

The Render filesystem is not intended to be permanent storage on free/ephemeral hosting. A production version should use persistent managed storage or an external database.

## 23. Security Note

For a production system:

- Do not hard-code Wi-Fi credentials in public source code.
- Store secrets in environment variables.
- Use secure TLS certificate validation instead of development-style insecure TLS settings.
- Add authentication and authorization to the API.
- Protect stored sensor/user data.

## 24. Testing Checklist

| Test | Expected result |
|---|---|
| FSR1 wiring | ADC value changes with pressure |
| FSR2 wiring | ADC value changes with pressure |
| FSR3 wiring | ADC value changes with pressure |
| FSR4 wiring | ADC value changes with pressure |
| DS18B20 | Valid temperature returned |
| Wi-Fi | ESP32 connects and reconnects if needed |
| HTTPS POST | Backend returns success |
| ML inference | Valid anomaly and risk output |
| Dashboard | Live data refreshes |
| 5-minute window | Recent readings appear |
| CSV download | Sensor data can be downloaded |
| Normal walking | Pattern remains within healthy reference behaviour when comparable |
| Controlled abnormal pressure | Mismatch can increase when pattern deviates strongly |

## 25. Limitations

- The prototype dataset is relatively small.
- The available reference dataset is primarily healthy-pattern data.
- FSR sensors provide relative/ADC-based pressure response and require calibration for physical pressure measurement.
- Sensor placement affects readings.
- Different users can produce different pressure distributions.
- Scenario coverage is limited by the collected dataset.
- The current firmware sends `Walking` as the scenario.
- The current mismatch-to-risk mapping is a project rule.
- The SQLite/CSV storage on Render is not durable across all redeployments/restarts.
- The system is not clinically validated.
- Diagnostic accuracy, sensitivity, specificity and clinical ulcer probability cannot be claimed from the current dataset.

## 26. Future Improvements

- Collect a larger and more diverse dataset.
- Include more healthy users and clinically labelled outcome data where appropriate.
- Add reliable calibration for physical pressure estimation.
- Improve sensor placement and mechanical integration.
- Add user-specific baseline calibration.
- Support multiple real-time activity/scenario modes.
- Add persistence logic for sustained abnormal conditions.
- Add stronger long-term storage.
- Add authentication and secure data handling.
- Add clinician/researcher analysis features.
- Perform formal validation before any medical use.

## 27. Project Deliverables

The completed project contains:

- Smart footwear hardware prototype
- ESP32 firmware
- FSR testing firmware
- DS18B20 testing firmware
- Structured sensor dataset
- Dataset repair/preprocessing workflow
- Healthy-reference ML training pipeline
- Saved ML model artifact
- ML inference pipeline
- FastAPI backend
- SQLite/CSV storage
- Render deployment configuration
- Streamlit real-time dashboard
- Risk indication and mismatch display
- Technical documentation
- Project procedure documentation

## 28. One-Line Project Summary

**An ESP32-based smart footwear prototype that measures multi-point foot pressure and temperature, sends 10-second averaged readings to an online FastAPI backend, compares them with healthy reference patterns using an Isolation Forest model, and displays the resulting ulcer-risk indication through a real-time Streamlit dashboard.**
