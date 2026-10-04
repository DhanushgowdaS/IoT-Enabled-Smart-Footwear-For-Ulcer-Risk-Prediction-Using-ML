from pathlib import Path
import csv
import io
import json
import re

import joblib
import numpy as np
import pandas as pd

from predict import predict

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "Data" / "footwear_dataset.csv"
MODEL_FILE = BASE_DIR / "ML" / "ulcer_risk_model.pkl"
REPORT_FILE = BASE_DIR / "ML" / "test_results.json"

def load_dataset(path):
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"(T\d{2}:\d{2}:\d{2})(?=\d+,(?:RAW|AVG10),Person\s)", r"\1\n", text)
    rows = list(csv.reader(io.StringIO(text)))
    df = pd.DataFrame([r for r in rows[1:] if len(r) == 10], columns=rows[0])
    for c in ["RecordNo", "FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["RecordNo", "FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]).copy()

def main():
    artifact = joblib.load(MODEL_FILE)
    assert {"model", "scaler", "thresholds", "feature_names"}.issubset(artifact), "Model artifact is incomplete"

    df = load_dataset(DATA_FILE)
    raw = df[df["Type"].eq("RAW")].copy()
    required = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]

    predictions = predict(raw[required])
    assert len(predictions) == len(raw)
    assert np.isfinite(predictions["AnomalyScore"]).all()
    assert ((predictions["MismatchPercent"] >= 0) & (predictions["MismatchPercent"] <= 100)).all()
    assert predictions["UlcerRisk"].isin(["Safe", "Low Risk", "Medium Risk", "High Risk"]).all()

    rng = np.random.default_rng(20261004)
    row = raw.iloc[int(rng.integers(0, len(raw)))]
    one = predict(pd.DataFrame([{c: row[c] for c in required}])).iloc[0]

    synthetic = pd.DataFrame([
        {"FSR1": 1500, "FSR2": 1200, "FSR3": 1800, "FSR4": 1300, "Temperature": 31.0},
        {"FSR1": 3500, "FSR2": 3000, "FSR3": 3400, "FSR4": 3200, "Temperature": 36.5},
        {"FSR1": 500, "FSR2": 900, "FSR3": 450, "FSR4": 700, "Temperature": 38.0},
    ])
    synthetic_predictions = predict(synthetic)
    assert len(synthetic_predictions) == 3
    assert np.isfinite(synthetic_predictions["AnomalyScore"]).all()

    result = {
        "status": "passed",
        "full_raw_prediction_rows": int(len(predictions)),
        "random_dataset_line": {
            "RecordNo": int(row["RecordNo"]),
            "Person": str(row["Person"]),
            "Scenario": str(row["Scenario"]),
            "FSR1": float(row["FSR1"]),
            "FSR2": float(row["FSR2"]),
            "FSR3": float(row["FSR3"]),
            "FSR4": float(row["FSR4"]),
            "Temperature": float(row["Temperature"]),
            "AnomalyScore": float(one["AnomalyScore"]),
            "HealthyMatchPercent": float(one["HealthyMatchPercent"]),
            "MismatchPercent": float(one["MismatchPercent"]),
            "UlcerRisk": str(one["UlcerRisk"]),
        },
        "synthetic_tests": synthetic_predictions.to_dict(orient="records"),
    }
    REPORT_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("MODEL TEST PASSED")
    print(f"Full RAW inference rows: {len(predictions)}")
    print(json.dumps(result["random_dataset_line"], indent=2))
    print(synthetic_predictions.to_string(index=False))
    print("Test report:", REPORT_FILE)

if __name__ == "__main__":
    main()
