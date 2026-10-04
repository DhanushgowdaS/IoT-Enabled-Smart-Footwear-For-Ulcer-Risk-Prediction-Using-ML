from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_FILE = Path(__file__).resolve().parent / "ulcer_risk_model.pkl"

ARTIFACT = joblib.load(MODEL_FILE)
MODEL = ARTIFACT["model"]
SCALER = ARTIFACT["scaler"]
THRESHOLDS = ARTIFACT["thresholds"]
SCENARIO_NAMES = ARTIFACT["scenario_names"]

REQUIRED = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]


def make_features(df):
    missing = [
        column
        for column in [*REQUIRED, "Scenario"]
        if column not in df.columns
    ]
    if missing:
        raise ValueError(f"Missing input columns: {missing}")

    scenarios = df["Scenario"].astype(str).tolist()
    unknown = sorted(set(scenarios) - set(SCENARIO_NAMES))

    if unknown:
        raise ValueError(f"Unknown scenario(s): {unknown}")

    fs = df[["FSR1", "FSR2", "FSR3", "FSR4"]].to_numpy(float)
    temp = df[["Temperature"]].to_numpy(float)

    total = fs.sum(axis=1)
    ratios = fs / (total[:, None] + 1.0)

    numeric = np.column_stack([
        fs,
        temp,
        total / 4.0,
        fs.max(axis=1),
        fs.min(axis=1),
        fs.std(axis=1),
        ratios,
    ])

    one_hot = np.array([
        [1.0 if scenario == known else 0.0 for known in SCENARIO_NAMES]
        for scenario in scenarios
    ])

    return np.column_stack([numeric, one_hot])


def predict(df, scenario=None):
    data = df.copy()

    if "Scenario" not in data.columns:
        if scenario is None:
            raise ValueError("Scenario is required for prediction")
        data["Scenario"] = scenario

    X = SCALER.transform(make_features(data))
    score = -MODEL.decision_function(X)

    denominator = THRESHOLDS["q99"] - THRESHOLDS["q95"]

    if denominator > 0:
        mismatch = np.clip(
            (score - THRESHOLDS["q95"]) / denominator * 100.0,
            0.0,
            100.0,
        )
    else:
        mismatch = np.zeros_like(score)

    risk = np.where(
        mismatch <= 10.0,
        "Safe",
        np.where(
            mismatch <= 33.333333,
            "Low Risk",
            np.where(
                mismatch <= 66.666667,
                "Medium Risk",
                "High Risk",
            ),
        ),
    )

    return pd.DataFrame({
        "AnomalyScore": score,
        "HealthyMatchPercent": 100.0 - mismatch,
        "MismatchPercent": mismatch,
        "UlcerRisk": risk,
    })
