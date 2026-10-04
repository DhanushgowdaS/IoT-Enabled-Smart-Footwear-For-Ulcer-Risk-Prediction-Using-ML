# ML and System Testing

## 1. Install Python packages

Create and activate a virtual environment, then install:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Check the trained ML model

The trained artifact must be present at:

```
ML/ulcer_risk_model.pkl
```

Run the complete ML test:

```bash
python ML/test_model.py
```

The test checks:

- Full RAW-dataset inference
- Valid anomaly scores
- Mismatch range from 0% to 100%
- Valid Safe/Low Risk/Medium Risk/High Risk output
- One deterministic random real dataset row
- Additional synthetic sensor patterns

## 3. Retrain the model

Run:

```bash
python ML/train_model.py
```

This:

1. Repairs the joined CSV records in memory.
2. Uses RAW data only.
3. Splits the data 80/10/10.
4. Fits StandardScaler on training data only.
5. Trains the Isolation Forest.
6. Calibrates q95, q98 and q99 on validation data.
7. Saves `ML/ulcer_risk_model.pkl`.
8. Writes `ML/model_validation_report.json`.

## 4. Test the FastAPI backend

Start the backend:

```bash
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

Use `POST /log` with:

```json
{
  "scenario": "Walking",
  "fsr1": 1500,
  "fsr2": 1200,
  "fsr3": 1800,
  "fsr4": 1300,
  "temp1": 31.0
}
```

The response should contain:

- anomaly_score
- healthy_match_percent
- mismatch_percent
- ulcer_risk

## 5. Test the dashboard

With FastAPI running:

Windows PowerShell:

```powershell
$env:API_URL="http://127.0.0.1:8000"
streamlit run app.py
```

Linux/macOS:

```bash
API_URL=http://127.0.0.1:8000 streamlit run app.py
```

The dashboard reads the API output and shows pressure, temperature, Healthy Match %, Mismatch %, and Ulcer Risk.

## Expected flow

```
Dataset
  ↓
train_model.py
  ↓
ulcer_risk_model.pkl
  ↓
ML/test_model.py
  ↓
FastAPI /log
  ↓
ML/predict.py
  ↓
SQLite + CSV
  ↓
Streamlit dashboard
```

The current ML stage is an unsupervised healthy-pattern deviation system. The supplied dataset does not contain true ulcer outcome labels, so this test process does not produce a clinical accuracy percentage.
