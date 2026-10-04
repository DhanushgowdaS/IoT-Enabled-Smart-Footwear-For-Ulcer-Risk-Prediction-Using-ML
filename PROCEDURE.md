# Complete Project Procedure

## IoT-Enabled Smart Footwear for Ulcer Risk Prediction Using Machine Learning

This document describes the complete development procedure followed for the implemented smart-footwear prototype, starting from selecting the sensing concept and hardware, continuing through electrical testing, firmware development, dataset preparation, Machine Learning, backend/API development, dashboard development, deployment and final end-to-end testing.

> **Scope:** This procedure documents the final implemented prototype. Earlier project concept documents described a larger sensor arrangement, but the final working hardware uses **4 FSR sensors and 1 DS18B20**, which matches the current firmware and backend.

---

## 1. Define the Project Requirement

The first step was to define what the footwear should measure and how the data should be used.

The required sensing parameters were:

- Foot pressure at multiple locations.
- Foot temperature.
- Continuous sensor acquisition.
- Wireless transmission.
- Remote data storage/processing.
- Machine-Learning-assisted risk indication.
- Real-time dashboard visualization.

The basic requirement was therefore converted into:

```text
Pressure + Temperature
        ↓
ESP32
        ↓
Wi-Fi
        ↓
Online Backend
        ↓
Machine Learning
        ↓
Risk Indication
        ↓
Dashboard
```

---

## 2. Select the Main Controller

### Component selected: ESP32

ESP32 was selected as the main controller because the project required:

- Multiple analog inputs for FSR sensors.
- Digital communication for the temperature sensor.
- Built-in Wi-Fi.
- Enough processing capability for sensor preprocessing.
- Easy programming using Arduino IDE.
- Direct integration with a web/API based IoT system.

The ESP32 therefore became the central controller for the entire embedded section.

---

## 3. Select the Pressure Sensors

### Component selected: FSR

Force Sensitive Resistors were selected for pressure sensing.

Reason for selection:

- Thin and suitable for an insole prototype.
- Resistance changes when force is applied.
- Can be placed underneath different foot regions.
- Can be read through the ESP32 ADC.
- Suitable for demonstrating pressure distribution.

The final prototype uses:

**4 × FSR sensors**

These are labelled:

- FSR1
- FSR2
- FSR3
- FSR4

---

## 4. Select the Temperature Sensor

### Component selected: DS18B20

The DS18B20 was selected because it provides digital temperature measurement through the OneWire protocol.

Advantages for the prototype:

- Digital output.
- Simple ESP32 interface.
- Suitable temperature measurement range for the prototype.
- Works with the OneWire and DallasTemperature Arduino libraries.

The final implementation uses:

**1 × DS18B20**

---

## 5. Select the Supporting Components

The supporting components were selected as follows:

| Component | Reason |
|---|---|
| 10 kΩ resistors × 4 | FSR voltage-divider circuits |
| 4.7 kΩ resistor | DS18B20 DATA pull-up |
| Battery / regulated supply | Portable/regulated power |
| On/off switch | System power control |
| Wires/connectors | Sensor-to-controller connections |
| Insole/base | Holds the sensors in position |

---

## 6. Final Hardware Connection Plan

The final GPIO mapping was selected based on the actual ESP32 implementation.

| ESP32 Pin | Device |
|---|---|
| GPIO34 | FSR1 |
| GPIO35 | FSR2 |
| GPIO32 | FSR3 |
| GPIO33 | FSR4 |
| GPIO4 | DS18B20 DATA |

The four FSR sensors use voltage dividers.

The DS18B20 DATA line uses a 4.7 kΩ pull-up resistor.

All connected components share the required electrical reference/common ground.

---

## 7. Build the FSR Voltage-Divider Circuits

Each FSR was connected as a voltage-divider circuit.

The purpose of the divider is to convert the FSR resistance change into a changing voltage that the ESP32 ADC can read.

Conceptually:

```text
Supply
  |
 FSR
  |
  +------→ ESP32 ADC
  |
 10 kΩ
  |
 GND
```

One divider is used for each FSR.

The important objective at this stage was not to calculate physical pressure in newtons, but to obtain a repeatable ADC response that changes with applied load.

---

## 8. Connect the DS18B20

The DS18B20 was connected using the OneWire bus.

```text
DS18B20
  |
  +---- DATA → ESP32 GPIO4
  |
  +---- 4.7 kΩ pull-up on DATA
```

The sensor supply and ground were connected correctly according to the sensor setup.

---

## 9. Perform Individual FSR Testing

Before writing the full project firmware, each pressure channel was tested separately.

File used:

`Firmware/FSR_testing_code.ino`

### Procedure

1. Connect the FSR circuits.
2. Upload the testing sketch.
3. Open Serial Monitor at 115200 baud.
4. Observe FSR1–FSR4 values.
5. Apply light pressure.
6. Apply stronger pressure.
7. Confirm that the corresponding ADC value changes.
8. Repeat for every sensor.

### Expected result

The sensor value should change when the corresponding FSR is loaded.

This test was important because an ADC/wiring error should be found before the ML and cloud stages.

---

## 10. Perform DS18B20 Testing

The temperature sensor was tested independently.

File used:

`Firmware/DS18B20_testing_code.ino`

### Procedure

1. Connect DS18B20.
2. Upload the test sketch.
3. Open Serial Monitor at 115200 baud.
4. Wait for the temperature reading.
5. Check that the sensor is detected.
6. Observe the temperature value.
7. Confirm that disconnecting the sensor produces the expected disconnected-sensor handling.

### Expected result

A valid temperature value should be displayed continuously.

---

## 11. Combine the Sensors

After individual testing:

- FSR1 was connected to GPIO34.
- FSR2 was connected to GPIO35.
- FSR3 was connected to GPIO32.
- FSR4 was connected to GPIO33.
- DS18B20 was connected to GPIO4.

The complete sensor set was then connected to one ESP32.

At this point the hardware layer was ready for firmware integration.

---

## 12. Develop the Main ESP32 Firmware

The final firmware file is:

`Firmware/Microcontrolle_ESP32_new_code.ino`

The firmware uses:

- WiFi
- WiFiClientSecure
- HTTPClient
- ArduinoJson
- OneWire
- DallasTemperature

The firmware was developed in stages:

1. Initialize serial communication.
2. Initialize the temperature sensor.
3. Configure the ESP32 for Wi-Fi.
4. Add Wi-Fi connection handling.
5. Read the FSR channels.
6. Read the DS18B20.
7. Add one-second sample timing.
8. Collect exactly 10 sensor samples.
9. Average the collected values.
10. Create JSON data.
11. Send the JSON to the backend.
12. Add retry handling for failed requests.

---

## 13. Final Sensor Sampling Method

The project eventually required live data to match the AVG10 format used in the reference dataset.

The final method is:

```text
Sample 1 → 1 second
Sample 2 → 1 second
Sample 3 → 1 second
...
Sample 10 → 1 second
        ↓
Average all valid samples
        ↓
One 10-second record
```

This is important because the ML model and live firmware now use the same time-window representation.

The firmware waits approximately one second between sampling events and sends after 10 samples have been collected.

---

## 14. Add Wi-Fi Communication

The ESP32 connects to the configured Wi-Fi network.

The firmware includes:

- Initial connection timeout.
- Automatic reconnect behaviour.
- Connection checking during operation.

If Wi-Fi is unavailable, the device attempts to reconnect before continuing transmission.

---

## 15. Add HTTPS Communication

The ESP32 sends data using HTTPS.

The backend endpoint used by the current firmware is:

`https://iot-enabled-smart-footwear-for-ulcer.onrender.com/log`

The sensor record is serialized into JSON.

Example:

```json
{
  "scenario": "Walking",
  "fsr1": 1500.0,
  "fsr2": 1200.0,
  "fsr3": 1600.0,
  "fsr4": 1300.0,
  "temp1": 32.0
}
```

The actual numeric values change with the sensor readings.

---

## 16. Add Transmission Retry Logic

Network requests can fail temporarily.

Therefore the final firmware retries the POST operation up to five times.

The implementation also includes:

- Request timeout.
- Wi-Fi reconnection before retry where required.
- Delay between attempts.
- Serial logging of the attempt number and HTTP response.

This improved reliability during live Render testing.

---

## 17. Collect the Reference Dataset

A structured dataset was used to develop the ML system.

The available reference data contains measurements from:

- Person A
- Person B

The dataset includes multiple scenarios such as:

- Standing
- Sitting
- Walking
- No_Load
- Toe_Pressure
- Heel_Pressure
- High_Pressure
- Right_Shift
- Left_Shift

The source file contains two record types:

- RAW
- AVG10

The final ML workflow uses AVG10 because live firmware also sends 10-second averages.

---

## 18. Repair the Dataset Format

During inspection, six physical CSV lines contained two records joined together.

Instead of manually rewriting the original source data, the training/test scripts repair the joined-record pattern in memory before parsing.

After repair:

- Physical lines including header: 6,098
- Logical records: 6,103

The logical dataset contains:

- 5,548 RAW records
- 555 AVG10 records

Only the AVG10 records are used for final model fitting.

---

## 19. Decide the Final ML Strategy

The initial project concept described a Random Forest classification workflow.

During final implementation, the available data and project requirement were reconsidered.

The supplied reference dataset did not provide dependable clinical ulcer/non-ulcer outcome labels for supervised medical classification.

Therefore the final strategy changed to:

**Healthy-pattern anomaly detection**

The final model is:

**StandardScaler + IsolationForest**

This allows the system to learn what the healthy reference data looks like and determine how unusual a new sensor pattern is.

---

## 20. Filter the ML Input

The training script selects only:

`Type == AVG10`

This produces the 555 10-second healthy reference windows used by the final ML pipeline.

RAW records are kept in the dataset but are not used to fit the final model.

This avoids the earlier problem where the model input format and live firmware input format were different.

---

## 21. Add Scenario Awareness

The final firmware sends a scenario value:

`Walking`

The dataset contains scenario labels.

The ML system therefore uses scenario as an additional feature.

The scenario is one-hot encoded.

Conceptually:

```text
Sensor values
   +
Scenario
   ↓
Feature vector
   ↓
ML model
```

This makes Walking readings comparable to healthy Walking patterns instead of mixing all activities into a single undifferentiated baseline.

---

## 22. Engineer the ML Features

For every AVG10 record, the software creates 13 numeric features.

### Raw sensor features

- FSR1
- FSR2
- FSR3
- FSR4
- Temperature

### Pressure summary features

- FSR Average
- FSR Maximum
- FSR Minimum
- FSR Standard Deviation

### Pressure distribution features

- FSR1 Ratio
- FSR2 Ratio
- FSR3 Ratio
- FSR4 Ratio

Then scenario one-hot features are added.

The resulting feature representation describes both absolute sensor values and the distribution of pressure across the insole.

---

## 23. Split the Data

The AVG10 records are split chronologically within each Person + Scenario group.

The target split is:

- 80% Training
- 10% Validation
- 10% Testing

For the current dataset this produces:

| Split | Rows |
|---|---:|
| Training | 444 |
| Validation | 55 |
| Testing | 56 |

The scaler is fitted only on the training data.

The validation data is used to calibrate the anomaly thresholds.

The test set remains held out for final stability checking.

---

## 24. Train the Scaler

The first ML processing stage is:

**StandardScaler**

The scaler puts the different model features onto a comparable numerical scale.

The scaler is fitted on the training subset only.

---

## 25. Train Isolation Forest

The final model uses:

- IsolationForest
- 500 trees
- `contamination="auto"`
- `random_state=42`
- Multi-core processing

The model is trained on the scaled healthy reference features.

The objective is to learn the structure of normal/healthy reference observations.

---

## 26. Generate Anomaly Scores

For inference, the Isolation Forest decision function is converted into the project's anomaly-score convention.

A higher anomaly score means greater deviation from the learned healthy pattern.

The same feature engineering and scaler used during training are used for live data.

---

## 27. Calibrate Validation Thresholds

The validation scores are used to calculate:

- q50
- q90
- q95
- q98
- q99

The important thresholds for mismatch conversion are q95 and q99.

This prevents the risk bands from being selected arbitrarily from individual live values.

---

## 28. Calculate Mismatch Percentage

For a new prediction:

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

Then:

```text
Healthy Match %
= 100 - Mismatch %
```

The mismatch value is a deviation index against the learned healthy reference pattern.

---

## 29. Convert Mismatch to Risk Indication

The current project mapping is:

| Mismatch | Indication |
|---:|---|
| 0–10% | Safe |
| >10–33.33% | Low Risk |
| >33.33–66.67% | Medium Risk |
| >66.67% | High Risk |

These are project-defined indication bands.

They are not clinical diagnostic thresholds.

---

## 30. Save the Trained Model

The training script saves the model artifact as:

`ML/ulcer_risk_model.pkl`

The artifact contains:

- Scaler
- Isolation Forest model
- Thresholds
- Scenario names
- Feature names
- Model version
- Training metadata
- Risk mapping

This allows the backend to reuse exactly the trained preprocessing/model pipeline.

---

## 31. Build the Inference Function

File:

`ML/predict.py`

The inference process is:

```text
Incoming FSR1–FSR4 + Temperature + Scenario
                  ↓
          Same feature engineering
                  ↓
             Saved scaler
                  ↓
          Saved Isolation Forest
                  ↓
             Anomaly score
                  ↓
             Mismatch %
                  ↓
          Healthy Match %
                  ↓
           Risk indication
```

The inference function checks that:

- Required columns exist.
- Scenario is known.
- Scores are finite.
- Output labels are valid.

---

## 32. Integrate ML with FastAPI

File:

`main.py`

When the ESP32 sends a new record:

1. FastAPI receives the JSON.
2. The data is placed into a Pandas DataFrame.
3. Scenario and sensor values are passed to `predict()`.
4. The ML result is returned.
5. Average pressure is calculated.
6. Maximum pressure is calculated.
7. A timestamp is generated.
8. The complete result is stored.
9. The processed result is returned to the ESP32.

The stored record contains both raw sensor values and ML results.

---

## 33. Add SQLite and CSV Storage

The backend keeps recent records in:

- SQLite
- CSV

The backend is configured to keep up to 500 readings.

The current storage fields include:

- Timestamp
- Scenario
- FSR1–FSR4
- Temperature
- Average pressure
- Maximum pressure
- Anomaly score
- Healthy Match %
- Mismatch %
- Ulcer Risk

---

## 34. Add the Latest-Reading Memory Layer

A latest-reading memory object was added to avoid an empty dashboard during some storage/restart situations.

The backend therefore supports:

- `/latest`
- `/data`

The latest reading can still be returned even when the local database has not yet populated the requested records.

---

## 35. Build the Streamlit Dashboard

File:

`app.py`

The dashboard was created after the API output fields were finalized.

The dashboard retrieves:

- `/data`
- `/latest`

The interface refreshes automatically every 5 seconds.

---

## 36. Add Pressure and Temperature Graphs

Two real-time visualizations were added.

### Pressure chart

Displays:

- FSR1
- FSR2
- FSR3
- FSR4

### Temperature chart

Displays:

- DS18B20 temperature

The charts use the recent data window.

---

## 37. Add Overall Risk Assessment

The dashboard evaluates the latest five-minute window.

It displays:

- Overall Risk Assessment
- Based on Readings from the Last 5 Minutes
- Number of readings in the last five minutes
- Latest mismatch percentage

This creates a recent-window summary instead of showing only a single instantaneous value.

---

## 38. Add Latest Entries Table

The dashboard also shows the latest 20 records.

The table contains:

- No.
- Timestamp
- Displayed risk status
- FSR1
- FSR2
- FSR3
- FSR4
- Temperature

---

## 39. Add CSV Download

The dashboard provides a sensor-data download button.

This lets the collected readings be exported for later analysis, reporting or future ML dataset expansion.

---

## 40. Deploy the Backend

Render was selected to host the FastAPI backend online.

The Render configuration is in:

`render.yaml`

The backend build process:

```text
Install Python dependencies
        ↓
Run ML/train_model.py
        ↓
Create saved model
        ↓
Start FastAPI with Uvicorn
```

The current deployed backend is:

`https://iot-enabled-smart-footwear-for-ulcer.onrender.com`

---

## 41. Configure the ESP32 for the Online Backend

The final ESP32 firmware uses the Render endpoint:

`https://iot-enabled-smart-footwear-for-ulcer.onrender.com/log`

After deployment:

1. Confirm the backend health endpoint.
2. Upload the latest firmware.
3. Open Serial Monitor.
4. Confirm Wi-Fi connection.
5. Confirm JSON generation.
6. Confirm HTTP response.
7. Check the dashboard for the new reading.

---

## 42. Handle Network Failures

During live integration, temporary connection failures can occur while the Render service restarts or wakes.

The final firmware therefore includes:

- Wi-Fi reconnect.
- Up to five POST attempts.
- 8-second HTTP timeout.
- 3-second delay between failed attempts.
- Serial logging of response status.

This makes the live system more tolerant of temporary network/service interruptions.

---

## 43. Verify Normal Walking

The final live workflow was tested with normal walking after aligning the firmware and ML model to the same 10-second AVG10 representation and adding scenario awareness.

The expected demonstration flow is:

```text
Normal walking
      ↓
ESP32 10-second average
      ↓
Walking scenario
      ↓
Healthy Walking baseline
      ↓
Low deviation
      ↓
Safe / Low Risk
```

The current working system no longer produces the earlier repeated false High Risk behaviour caused by the training/live input mismatch.

---

## 44. Perform a Controlled Abnormal-Pressure Demonstration

For an external project demonstration, the footwear can be loaded in an intentionally abnormal pattern.

The easiest method is localized pressure:

```text
FSR1 = strong
FSR2 = low
FSR3 = low
FSR4 = low
```

or the reverse/shifted pattern:

```text
FSR1 = low
FSR2 = low
FSR3 = strong
FSR4 = low
```

The pressure should be held for at least one complete 10-second collection window.

The purpose is to produce a pressure distribution that differs strongly from the healthy reference.

A large deviation can therefore move the displayed mismatch toward the High Risk band.

This is a demonstration of abnormal-pattern detection, not proof of an actual ulcer.

---

## 45. Run Final ML Tests

The repository provides:

`ML/test_model.py`

The final test should verify:

- Model artifact loads correctly.
- AVG10 inputs pass through the inference function.
- Scores are finite.
- Mismatch is between 0 and 100%.
- Risk labels are valid.

The random test file can also be used to exercise the prediction function with synthetic sensor combinations.

---

## 46. Perform End-to-End Testing

The complete system should be tested in this order:

### Hardware

- [ ] FSR1 responds.
- [ ] FSR2 responds.
- [ ] FSR3 responds.
- [ ] FSR4 responds.
- [ ] DS18B20 responds.
- [ ] Supply is stable.
- [ ] Sensor wiring is secure.

### Firmware

- [ ] ESP32 starts.
- [ ] Wi-Fi connects.
- [ ] Sensor readings are visible.
- [ ] 10 samples are collected.
- [ ] 10-second averages are produced.
- [ ] JSON is created.
- [ ] HTTPS POST succeeds.
- [ ] Retry logic works if the network is temporarily unavailable.

### Backend

- [ ] `/` returns API health.
- [ ] `/log` accepts sensor input.
- [ ] ML output is generated.
- [ ] Data is stored.
- [ ] `/latest` returns the newest record.
- [ ] `/data` returns recent records.
- [ ] CSV download works.

### Machine Learning

- [ ] AVG10 data is used.
- [ ] Scenario is included.
- [ ] Feature engineering matches training and inference.
- [ ] Mismatch stays within 0–100%.
- [ ] Risk label is valid.

### Dashboard

- [ ] Dashboard connects.
- [ ] Pressure graph updates.
- [ ] Temperature graph updates.
- [ ] Overall Risk Assessment updates.
- [ ] Five-minute readings are shown.
- [ ] Latest 20 table updates.
- [ ] CSV export works.

---

## 47. Final Working Pipeline

The complete implemented system is:

```text
4 × FSR + DS18B20
        ↓
     ESP32
        ↓
10 samples / 10 seconds
        ↓
10-second average (AVG10)
        ↓
HTTPS JSON
        ↓
FastAPI on Render
        ↓
Scenario-aware feature engineering
        ↓
StandardScaler
        ↓
Isolation Forest
        ↓
Anomaly Score
        ↓
Mismatch %
        ↓
Healthy Match %
        ↓
Safe / Low / Medium / High indication
        ↓
SQLite + CSV
        ↓
Streamlit
        ↓
5-minute overall assessment
+ latest 20 readings
+ pressure/temperature trends
```

---

## 48. Final Project Outcome

The project now provides an end-to-end working prototype that connects the physical sensing layer to an online ML-enabled monitoring dashboard.

The final implementation includes:

- Physical pressure sensing.
- Temperature sensing.
- ESP32 embedded acquisition.
- 10-second synchronized averaging.
- Wi-Fi/HTTPS communication.
- FastAPI backend.
- ML inference.
- Healthy-pattern mismatch calculation.
- Risk indication.
- SQLite/CSV storage.
- Render backend deployment.
- Streamlit live dashboard.
- Five-minute overall assessment.
- CSV data export.

---

## 49. Important Limitations

The final prototype should be presented honestly.

### Dataset limitation

The available dataset is small and based on healthy reference measurements. It is not a clinically validated medical dataset.

### Sensor limitation

FSR values are relative ADC responses unless calibrated against a suitable pressure/force reference.

### Model limitation

Isolation Forest learns healthy structure; it does not prove that a user has a clinical ulcer.

### Risk limitation

The project's Safe/Low/Medium/High bands are software-defined interpretation levels.

### Clinical limitation

The system cannot currently claim:

- clinical diagnosis,
- clinical ulcer probability,
- sensitivity,
- specificity,
- medically validated accuracy.

---

## 50. Future Development

The next technical improvements would be:

1. Expand the dataset with more users and sessions.
2. Add carefully labelled clinical outcomes where ethically and legally appropriate.
3. Calibrate FSR readings into meaningful physical pressure measurements.
4. Improve sensor placement and mechanical design.
5. Add user-specific healthy baselines.
6. Add sustained-condition logic across multiple windows.
7. Add persistent external database storage.
8. Add secure authentication and API protection.
9. Add multiple activity/scenario modes.
10. Perform formal validation before any medical application.

---

## 51. Final Documentation Rule

The repository should always describe the **implemented system**, not an earlier planned version.

The current final implementation is:

**4 FSR + 1 DS18B20 + ESP32 + Wi-Fi + FastAPI + Isolation Forest healthy-baseline ML + Render + Streamlit**

and the live sensor-processing format is:

**10 one-second samples → one 10-second AVG10 record**

This keeps the hardware, firmware, dataset, ML model, backend and dashboard descriptions consistent.
