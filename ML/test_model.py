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

    text = re.sub(
        r"(T\d{2}:\d{2}:\d{2})(?=\d+,(?:RAW|AVG10),Person\s)",
        r"\1\n",
        text,
    )

    rows = list(csv.reader(io.StringIO(text)))
    header = rows[0]

    valid = [
        row
        for row in rows[1:]
        if len(row) == len(header)
    ]

    df = pd.DataFrame(valid, columns=header)

    for column in [
        "RecordNo",
        "FSR1",
        "FSR2",
        "FSR3",
        "FSR4",
        "Temperature",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df.dropna(
        subset=[
            "RecordNo",
            "FSR1",
            "FSR2",
            "FSR3",
            "FSR4",
            "Temperature",
        ]
    ).copy()


def main():
    artifact = joblib.load(MODEL_FILE)

    assert {
        "model",
        "scaler",
        "thresholds",
        "feature_names",
        "scenario_names",
    }.issubset(artifact), "Model artifact is incomplete"

    df = load_dataset(DATA_FILE)
    avg10 = df[df["Type"].eq("AVG10")].copy()

    columns = [
        "Scenario",
        "FSR1",
        "FSR2",
        "FSR3",
        "FSR4",
        "Temperature",
    ]

    predictions = predict(avg10[columns])

    assert len(predictions) == len(avg10)
    assert np.isfinite(predictions["AnomalyScore"]).all()
    assert predictions["MismatchPercent"].between(0, 100).all()
    assert predictions["UlcerRisk"].isin([
        "Safe",
        "Low Risk",
        "Medium Risk",
        "High Risk",
    ]).all()

    walking = avg10[avg10["Scenario"].eq("Walking")].copy()
    walking_predictions = predict(walking[columns])

    risk_counts = walking_predictions["UlcerRisk"].value_counts().to_dict()

    result = {
        "status": "passed",
        "model_version": artifact["model_version"],
        "full_avg10_prediction_rows": int(len(predictions)),
        "walking_avg10_rows": int(len(walking)),
        "walking_risk_counts": {
            label: int(risk_counts.get(label, 0))
            for label in [
                "Safe",
                "Low Risk",
                "Medium Risk",
                "High Risk",
            ]
        },
        "scenarios_tested": artifact["scenario_names"],
    }

    REPORT_FILE.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("MODEL TEST PASSED")
    print(json.dumps(result, indent=2))
    print("Test report:", REPORT_FILE)


if __name__ == "__main__":
    main()
