# Dataset Repair & ML Procedure

## 1. Purpose

This document records the work done to inspect, repair, validate, and prepare the Smart Footwear dataset for ML work.

Repository:
DhanushgowdaS/IoT-Enabled-Smart-Footwear-For-Ulcer-Risk-Prediction-Using-ML

Local project folder used:
C:\Users\Amith\OneDrive\Desktop\ML\IoT-Enabled-Smart-Footwear-For-Ulcer-Risk-Prediction-Using-ML-main

---

## 2. What We Found

The original dataset was:

`footwear_dataset.csv`

Expected columns:

`RecordNo, Type, Person, Scenario, FSR1, FSR2, FSR3, FSR4, Temperature, LoggedAt`

The original file contained 6097 physical data lines.

Some records were accidentally joined together because a newline was missing between two records. This caused lines such as:

`2415,...,2026-10-02T19:59:562416,RAW,...`

The same issue was found at physical lines:

- 1000
- 1999
- 2998
- 3997
- 4996
- 5995

The problem was a CSV structure problem, not missing sensor values.

---

## 3. Why We Repaired the Dataset

The joined records could cause:

- incorrect CSV parsing
- wrong column counts
- corrupted RecordNo/LoggedAt fields
- incorrect ML training input
- incorrect statistics and validation

Therefore, the records had to be separated before using the dataset for ML.

---

## 4. Repair Script

A new script was created:

`repair_dataset.py`

Its job is to:

1. Read `footwear_dataset.csv`
2. Detect multiple records accidentally joined on one physical line
3. Split those records using the record-start pattern
4. Parse each repaired record as CSV
5. Validate that each record has exactly 10 columns
6. Preserve sensor values, including `0` and `4095`
7. Write the repaired dataset to:
   `footwear_dataset_repaired.csv`

The script was added to GitHub.

---

## 5. Commands Used

Open PowerShell in the project directory:

```powershell
cd "C:\Users\Amith\OneDrive\Desktop\ML\IoT-Enabled-Smart-Footwear-For-Ulcer-Risk-Prediction-Using-ML-main"
```

Activate the Python virtual environment:

```powershell
.\.venv313\Scripts\Activate.ps1
```

Run the repair:

```powershell
python repair_dataset.py
```

Expected repair result:

```
=== DATASET REPAIR ===
Original physical data lines: 6097
Repaired logical records: 6103
Skipped malformed records: 0
Output: footwear_dataset_repaired.csv
```

---

## 6. Repair Result

The repaired dataset contains:

- 6103 logical data records
- 10 columns
- 0 skipped malformed records

The increase from 6097 physical lines to 6103 logical records is because 6 physical lines contained two joined records.

Therefore:

`6097 + 6 = 6103`

---

## 7. Dataset Validation

The repaired CSV was loaded and checked.

Columns:

```
RecordNo
Type
Person
Scenario
FSR1
FSR2
FSR3
FSR4
Temperature
LoggedAt
```

Type counts:

```
RAW      5548
AVG10     555
```

Person counts:

```
Person A    3133
Person B    2970
```

Scenario counts:

```
Right_Shift      990
No_Load          824
Standing          660
Walking           660
Sitting           660
High_Pressure     660
Heel_Pressure     660
Toe_Pressure      659
Left_Shift        330
```

---

## 8. AVG10 Validation

There are 555 AVG10 records.

Checks performed:

- missing values: 0
- duplicate rows: 0
- duplicate RecordNo: 0

AVG10 by person:

```
Person A    285
Person B    270
```

AVG10 by scenario:

```
Right_Shift       90
No_Load           75
Standing          60
Walking           60
Sitting           60
Toe_Pressure      60
Heel_Pressure     60
High_Pressure     60
Left_Shift        30
```

The repaired dataset passed these structural checks.

---

## 9. Important ML File Distinction

During the investigation, it was found that `train_model.py` is not the current/main production ML model.

The current backend loads:

`model.pkl`

The relevant backend logic is:

```python
MODEL = joblib.load("model.pkl")
```

and prediction is performed using:

```python
prediction = str(MODEL.predict(features)[0])
```

Therefore, `model.pkl` is the model currently used by the FastAPI backend.

Do NOT replace or modify `model.pkl` until its structure, features, classes, and performance have been inspected and tested.

---

## 10. Old Test Training Script

`train_model.py` was inspected.

It uses:

- `dataset.xlsx`
- RandomForestClassifier
- 200 estimators
- old scenario names
- a `risk_map`
- output file `ulcer_model.pkl`

This script is different from the current backend model workflow.

It should therefore be treated as an older/test training script unless later verification shows otherwise.

---

## 11. Python Dependencies

The project requirements include:

```
fastapi
uvicorn
pandas
scikit-learn
joblib
requests
plotly
streamlit-autorefresh
```

When attempting to inspect `model.pkl`, the environment initially returned:

```
ModuleNotFoundError: No module named 'joblib'
```

This means the current virtual environment did not yet have all required packages installed.

Install the project requirements with:

```powershell
pip install -r requirements.txt
```

Then model inspection can be performed.

---

## 12. GitHub Update Procedure

GitHub is treated as the project source of truth.

Repository:

DhanushgowdaS/IoT-Enabled-Smart-Footwear-For-Ulcer-Risk-Prediction-Using-ML

The repair script was added to the repository as:

`repair_dataset.py`

The repaired CSV:

`footwear_dataset_repaired.csv`

has been created locally but has NOT yet been uploaded to GitHub.

The CSV will be uploaded later after providing the file to the working environment.

---

## 13. Current Status

### Completed

- Identified the malformed joined CSV records
- Identified all 6 affected physical lines
- Created the repair script
- Repaired the dataset locally
- Produced 6103 logical records
- Confirmed 0 malformed records were skipped
- Validated columns and record types
- Validated Person distribution
- Validated Scenario distribution
- Validated AVG10 records
- Confirmed `model.pkl` is loaded by `main.py`
- Confirmed `train_model.py` is an older/test training workflow
- Added `repair_dataset.py` to GitHub

### Pending

- Upload `footwear_dataset_repaired.csv` to GitHub
- Install/verify Python dependencies if not already installed
- Inspect `model.pkl`
- Verify model input features
- Verify model output/classes
- Test the current model against the repaired dataset
- Only after verification, decide whether model retraining or replacement is required

---

## 14. Important Rule Going Forward

Do not overwrite the current `model.pkl` or production ML workflow blindly.

First:

1. Inspect the existing model.
2. Identify its expected input features.
3. Identify its output classes.
4. Test it.
5. Compare results with the repaired dataset.
6. Then decide whether any ML changes are required.

This keeps the existing Smart Footwear application working while the dataset and ML pipeline are being improved.
