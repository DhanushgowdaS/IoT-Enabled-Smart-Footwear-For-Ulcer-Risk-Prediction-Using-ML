from pathlib import Path
import joblib
import numpy as np
import pandas as pd

MODEL_FILE = Path(__file__).resolve().parent / "ulcer_risk_model.pkl"
ARTIFACT = joblib.load(MODEL_FILE)
MODEL = ARTIFACT["model"]
SCALER = ARTIFACT["scaler"]
THRESHOLDS = ARTIFACT["thresholds"]
REQUIRED = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]

def make_features(df):
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing input columns: {missing}")
    fs = df[["FSR1", "FSR2", "FSR3", "FSR4"]].to_numpy(float)
    temp = df[["Temperature"]].to_numpy(float)
    total = fs.sum(axis=1)
    ratios = fs / (total[:, None] + 1.0)
    return np.column_stack([
        fs, temp, total / 4.0, fs.max(axis=1), fs.min(axis=1),
        fs.std(axis=1), ratios
    ])

def predict(df):
    X = SCALER.transform(make_features(df))
    score = -MODEL.decision_function(X)
    denominator = THRESHOLDS["q99"] - THRESHOLDS["q95"]
    mismatch = np.clip(
        (score - THRESHOLDS["q95"]) / denominator * 100.0, 0.0, 100.0
    ) if denominator > 0 else np.zeros_like(score)
    risk = np.where(
        score <= THRESHOLDS["q95"], "Safe",
        np.where(
            score <= THRESHOLDS["q98"], "Low Risk",
            np.where(score <= THRESHOLDS["q99"], "Medium Risk", "High Risk")
        )
    )
    return pd.DataFrame({
        "AnomalyScore": score,
        "HealthyMatchPercent": 100.0 - mismatch,
        "MismatchPercent": mismatch,
        "UlcerRisk": risk,
    })
