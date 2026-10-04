from pathlib import Path
import csv
import io
import json
import re

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "Data" / "footwear_dataset.csv"
MODEL_FILE = BASE_DIR / "ML" / "ulcer_risk_model.pkl"
REPORT_FILE = BASE_DIR / "ML" / "model_validation_report.json"

RAW_FEATURES = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]
FEATURES = RAW_FEATURES + [
    "FSR_Average", "FSR_Max", "FSR_Min", "FSR_STD",
    "FSR1_Ratio", "FSR2_Ratio", "FSR3_Ratio", "FSR4_Ratio"
]

def load_dataset(path):
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines:
        raise ValueError("Dataset is empty")
    text = re.sub(r"(T\d{2}:\d{2}:\d{2})(?=\d+,(?:RAW|AVG10),Person\s)", r"\1\n", text)
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[0]
    valid = [r for r in rows[1:] if len(r) == len(header)]
    if len(valid) != len(rows) - 1:
        raise ValueError("Dataset repair produced invalid rows")
    df = pd.DataFrame(valid, columns=header)
    for c in ["RecordNo", *RAW_FEATURES]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["LoggedAt"] = pd.to_datetime(df["LoggedAt"], errors="coerce")
    return df.dropna(subset=["RecordNo", *RAW_FEATURES, "LoggedAt"]).copy()

def make_features(df):
    fs = df[["FSR1", "FSR2", "FSR3", "FSR4"]].to_numpy(float)
    temp = df[["Temperature"]].to_numpy(float)
    total = fs.sum(axis=1)
    ratios = fs / (total[:, None] + 1.0)
    return np.column_stack([
        fs, temp, total / 4.0, fs.max(axis=1), fs.min(axis=1),
        fs.std(axis=1), ratios
    ])

def split_80_10_10(df):
    parts = []
    for (_, _), group in df.sort_values(["Person", "Scenario", "RecordNo"]).groupby(["Person", "Scenario"], sort=False):
        n = len(group)
        n_train = round(n * 0.80)
        n_val = round(n * 0.10)
        train = group.iloc[:n_train].copy()
        val = group.iloc[n_train:n_train + n_val].copy()
        test = group.iloc[n_train + n_val:].copy()
        train["Split"] = "train"
        val["Split"] = "validation"
        test["Split"] = "test"
        parts.extend([train, val, test])
    return pd.concat(parts, ignore_index=True)

def get_scores(model, scaler, df):
    return -model.decision_function(scaler.transform(make_features(df)))

def main():
    df = load_dataset(DATA_FILE)
    raw = df[df["Type"].eq("RAW")].copy()
    if raw.empty:
        raise ValueError("No RAW records found")

    splits = split_80_10_10(raw)
    train = splits[splits["Split"].eq("train")].copy()
    validation = splits[splits["Split"].eq("validation")].copy()
    test = splits[splits["Split"].eq("test")].copy()

    scaler = StandardScaler()
    X_train = scaler.fit_transform(make_features(train))

    model = IsolationForest(
        n_estimators=500,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train)

    validation_scores = get_scores(model, scaler, validation)
    q50, q90, q95, q98, q99 = np.percentile(validation_scores, [50, 90, 95, 98, 99])
    thresholds = {
        "q50": float(q50), "q90": float(q90), "q95": float(q95),
        "q98": float(q98), "q99": float(q99)
    }

    test_scores = get_scores(model, scaler, test)
    full_scores = get_scores(model, scaler, raw)
    if not np.isfinite(full_scores).all():
        raise ValueError("Non-finite prediction found")

    risk_counts = {
        "Safe": int(np.sum(test_scores <= thresholds["q95"])),
        "Low Risk": int(np.sum((test_scores > thresholds["q95"]) & (test_scores <= thresholds["q98"]))),
        "Medium Risk": int(np.sum((test_scores > thresholds["q98"]) & (test_scores <= thresholds["q99"]))),
        "High Risk": int(np.sum(test_scores > thresholds["q99"])),
    }

    report = {
        "status": "passed",
        "dataset": {
            "physical_lines": int(len(DATA_FILE.read_text(encoding="utf-8-sig").splitlines())),
            "logical_rows_after_repair": int(len(df)),
            "raw_rows_used": int(len(raw)),
            "avg10_rows_excluded": int((df["Type"] == "AVG10").sum()),
        },
        "split": {
            "train": int(len(train)),
            "validation": int(len(validation)),
            "test": int(len(test)),
            "train_percent": float(len(train) / len(raw) * 100),
            "validation_percent": float(len(validation) / len(raw) * 100),
            "test_percent": float(len(test) / len(raw) * 100),
            "method": "Chronological split within each Person+Scenario group",
        },
        "validation_thresholds": thresholds,
        "test_healthy_stability": {
            "above_q95_percent": float(np.mean(test_scores > thresholds["q95"]) * 100),
            "above_q98_percent": float(np.mean(test_scores > thresholds["q98"]) * 100),
            "above_q99_percent": float(np.mean(test_scores > thresholds["q99"]) * 100),
            "risk_counts": risk_counts,
        },
        "notes": [
            "The dataset contains healthy reference subjects only; no true ulcer/non-ulcer labels are available.",
            "Therefore, accuracy, sensitivity, specificity, and clinical diagnostic performance cannot be computed from this dataset.",
            "q95/q98/q99 are healthy-reference anomaly thresholds calibrated on the validation split only.",
            "Mismatch percent is a healthy-pattern deviation index, not ulcer probability."
        ],
    }

    artifact = {
        "model_version": "healthy-baseline-v1",
        "model_type": "IsolationForest",
        "purpose": "Healthy-pattern anomaly detection for ulcer-risk indication",
        "feature_names": FEATURES,
        "scaler": scaler,
        "model": model,
        "thresholds": thresholds,
        "risk_rule": {
            "Safe": "score <= q95",
            "Low Risk": "q95 < score <= q98",
            "Medium Risk": "q98 < score <= q99",
            "High Risk": "score > q99"
        },
        "mismatch_rule": "clip((score - q95) / (q99 - q95) * 100, 0, 100)",
        "training_type": "RAW only",
        "dataset_logical_rows": int(len(df)),
        "raw_rows": int(len(raw)),
        "avg10_rows_excluded": int((df["Type"] == "AVG10").sum()),
        "split_counts": {"train": int(len(train)), "validation": int(len(validation)), "test": int(len(test))},
        "persons": sorted(raw["Person"].astype(str).unique().tolist()),
        "scenarios": sorted(raw["Scenario"].astype(str).unique().tolist()),
    }

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, MODEL_FILE)
    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("MODEL BUILD PASSED")
    print(f"Logical rows: {len(df)}")
    print(f"RAW rows used: {len(raw)}")
    print(f"Excluded AVG10: {(df['Type'] == 'AVG10').sum()}")
    print(f"Split: train={len(train)}, validation={len(validation)}, test={len(test)}")
    print("Validation thresholds:", json.dumps(thresholds, indent=2))
    print("Healthy test rates:", json.dumps(report["test_healthy_stability"], indent=2))
    print("Model saved:", MODEL_FILE)

if __name__ == "__main__":
    main()
