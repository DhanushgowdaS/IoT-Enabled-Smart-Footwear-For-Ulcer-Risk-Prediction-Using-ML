# Smart Footwear - New ML Pipeline

## 1. Purpose

This folder contains the new machine-learning pipeline for the IoT-enabled smart footwear project.

The purpose of this pipeline is to convert the repaired footwear sensor dataset into machine-learning data, train a new risk-classification model, evaluate it, and prepare it for integration with the backend and dashboard.

The new pipeline is independent of the old `model.pkl`.

---

## 2. Input Dataset

The main input dataset is:

`Data/CSV/footwear_dataset_repaired.csv`

It contains:

- FSR1
- FSR2
- FSR3
- FSR4
- Temperature
- Person
- Scenario
- RecordNo
- LoggedAt
- Type

The dataset contains 6,103 records.

---

## 3. Dataset Validation

Before machine-learning training, the dataset is checked for:

- Missing values
- Duplicate records
- Duplicate RecordNo values
- Invalid temperature values
- FSR sensor extremes
- Record number anomalies
- RAW and AVG10 record structure

RecordNo is treated as metadata and is not used as an ML feature.

---

## 4. Feature Engineering

The new pipeline creates additional pressure-related features from the four FSR sensors.

Features include:

- Pressure_Mean
- Pressure_Max
- Pressure_Min
- Pressure_Std
- Total_Pressure
- Pressure_Range
- Left_Load
- Right_Load
- Left_Right_Imbalance
- Max_Pressure_Ratio
- High_Load_Sensors

The original FSR values and Temperature are also retained.

---

## 5. Risk Classes

The current prototype uses the recorded Scenario information to create four risk categories.

| Scenario | Prototype Risk |
|---|---|
| No_Load | SAFE |
| Sitting | SAFE |
| Walking | LOW |
| Standing | LOW |
| Left_Shift | MEDIUM |
| Right_Shift | MEDIUM |
| Heel_Pressure | MEDIUM |
| Toe_Pressure | MEDIUM |
| High_Pressure | HIGH |

These are prototype labels derived from controlled sensor scenarios.

They are not clinical diagnoses and have not been clinically validated as diabetic-foot-ulcer labels.

---

## 6. Prepared ML Dataset

The preparation script is:

`ML/prepare_new_ml_dataset.py`

It creates:

`Data/CSV/new_ml_dataset.csv`

Current dataset:

- Rows: 6,103
- ML features: 16
- Target: Risk
- Classes: SAFE, LOW, MEDIUM, HIGH

---

## 7. Training Procedure

The next stage is to train multiple machine-learning algorithms using the prepared dataset.

The models will be compared using:

- Accuracy
- Balanced Accuracy
- Precision
- Recall
- Macro F1-score
- Weighted F1-score
- Confusion Matrix

The model with the most suitable validation performance will be selected.

---

## 8. Model Validation

The data split must avoid unnecessary leakage between highly related sensor records.

The model should not use:

- Scenario
- Person
- RecordNo
- LoggedAt

as prediction features.

These fields are metadata or label-generation information.

---

## 9. New Model

The new trained model will be saved separately from the old:

`model.pkl`

The old model will not be overwritten until the new pipeline has been tested and approved.

---

## 10. System Integration

After model validation, the new model will be connected to:

Backend:

`Backend/main.py`

Dashboard:

`Dashboard/app.py`

The final system will follow:

Sensor Data
→ Feature Engineering
→ ML Model
→ Risk Prediction
→ Backend
→ Dashboard

---

## 11. Development Procedure

1. Validate repaired dataset
2. Prepare ML dataset
3. Verify feature and risk distributions
4. Train multiple models
5. Validate models
6. Select and save the new model
7. Test model predictions
8. Integrate model with backend
9. Update dashboard
10. Test using live ESP32 data
11. Update GitHub

---

## 12. Important Limitation

This project is currently a prototype based on controlled footwear sensor scenarios.

The generated risk classes should not be presented as clinically validated ulcer diagnosis or medical prediction without appropriate clinical datasets and validation.
