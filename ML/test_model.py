from pathlib import Path
import joblib
import numpy as np
import pandas as pd

MODEL_FILE = Path("ML/ulcer_risk_model.pkl")
artifact = joblib.load(MODEL_FILE)

model = artifact["model"]
scaler = artifact["scaler"]
cal = artifact["calibration"]

def make_features(df):
    fs = df[["FSR1","FSR2","FSR3","FSR4"]].to_numpy(float)
    temp = df[["Temperature"]].to_numpy(float)
    total = fs.sum(axis=1)
    ratios = fs / (total[:, None] + 1.0)
    return np.column_stack([
        fs,
        temp,
        total / 4.0,
        fs.max(axis=1),
        fs.min(axis=1),
        fs.std(axis=1),
        ratios
    ])

def predict(df):
    X = scaler.transform(make_features(df))
    anomaly = -model.decision_function(X)
    mismatch = np.clip(
        (anomaly - cal["q95"]) /
        (cal["q99"] - cal["q95"]) * 100,
        0,
        100
    )
    risk = np.select(
        [mismatch <= 0, mismatch <= 33.333333, mismatch <= 66.666667],
        ["Safe", "Low Risk", "Medium Risk"],
        default="High Risk"
    )
    return pd.DataFrame({
        "AnomalyScore": anomaly,
        "MismatchPercent": mismatch,
        "UlcerRisk": risk
    })

sample = pd.DataFrame([{
    "FSR1": 2000,
    "FSR2": 1500,
    "FSR3": 2500,
    "FSR4": 1800,
    "Temperature": 31.0
}])

print(predict(sample).to_string(index=False))
