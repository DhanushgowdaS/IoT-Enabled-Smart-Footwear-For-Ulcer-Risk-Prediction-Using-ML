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
NUMERIC_FEATURES = RAW_FEATURES + [
    "FSR_Average",
    "FSR_Max",
    "FSR_Min",
    "FSR_STD",
    "FSR1_Ratio",
    "FSR2_Ratio",
    "FSR3_Ratio",
    "FSR4_Ratio",
]


def load_dataset(path):
    text = path.read_text(encoding="utf-8-sig")

    if not text.strip():
        raise ValueError("Dataset is empty")

    text = re.sub(
        r"(T\d{2}:\d{2}:\d{2})(?=\d+,(?:RAW|AVG10),Person\s)",
        r"\1\n",
        text,
    )

    rows = list(csv.reader(io.StringIO(text)))
    header = rows[0]

    valid = [row for row in rows[1:] if len(row) == len(header)]

    if len(valid) != len(rows) - 1:
        raise ValueError("Dataset repair produced invalid rows")

    df = pd.DataFrame(valid, columns=header)

    for column in ["RecordNo", *RAW_FEATURES]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["LoggedAt"] = pd.to_datetime(df["LoggedAt"], errors="coerce")

    return df.dropna(
        subset=["RecordNo", *RAW_FEATURES, "LoggedAt"]
    ).copy()


def numeric_features(df):
    fs = df[["FSR1", "FSR2", "FSR3", "FSR4"]].to_numpy(float)
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
        ratios,
    ])


def make_features(df, scenario_names):
    missing = [
        column
        for column in ["Scenario", *RAW_FEATURES]
        if column not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing input columns: {missing}")

    numeric = numeric_features(df)

    scenarios = df["Scenario"].astype(str).tolist()

    unknown = sorted(set(scenarios) - set(scenario_names))

    if unknown:
        raise ValueError(f"Unknown scenarios: {unknown}")

    one_hot = np.array([
        [
            1.0 if scenario == known else 0.0
            for known in scenario_names
        ]
        for scenario in scenarios
    ])

    return np.column_stack([numeric, one_hot])


def split_80_10_10(df):
    parts = []

    for _, group in df.sort_values(
        ["Person", "Scenario", "RecordNo"]
    ).groupby(["Person", "Scenario"], sort=False):

        count = len(group)
        train_count = round(count * 0.80)
        validation_count = round(count * 0.10)

        train = group.iloc[:train_count].copy()
        validation = group.iloc[
            train_count:train_count + validation_count
        ].copy()
        test = group.iloc[
            train_count + validation_count:
        ].copy()

        train["Split"] = "train"
        validation["Split"] = "validation"
        test["Split"] = "test"

        parts.extend([train, validation, test])

    return pd.concat(parts, ignore_index=True)


def get_scores(model, scaler, df, scenario_names):
    features = make_features(df, scenario_names)
    return -model.decision_function(scaler.transform(features))


def main():
    df = load_dataset(DATA_FILE)

    avg10 = df[df["Type"].eq("AVG10")].copy()

    if avg10.empty:
        raise ValueError("No AVG10 records found")

    scenario_names = sorted(
        avg10["Scenario"].astype(str).unique().tolist()
    )

    splits = split_80_10_10(avg10)

    train = splits[splits["Split"].eq("train")].copy()
    validation = splits[splits["Split"].eq("validation")].copy()
    test = splits[splits["Split"].eq("test")].copy()

    scaler = StandardScaler()

    X_train = scaler.fit_transform(
        make_features(train, scenario_names)
    )

    model = IsolationForest(
        n_estimators=500,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train)

    validation_scores = get_scores(
        model,
        scaler,
        validation,
        scenario_names,
    )

    q50, q90, q95, q98, q99 = np.percentile(
        validation_scores,
        [50, 90, 95, 98, 99],
    )

    thresholds = {
        "q50": float(q50),
        "q90": float(q90),
        "q95": float(q95),
        "q98": float(q98),
        "q99": float(q99),
    }

    test_scores = get_scores(
        model,
        scaler,
        test,
        scenario_names,
    )

    mismatch = np.clip(
        (
            (test_scores - thresholds["q95"])
            / (thresholds["q99"] - thresholds["q95"])
            * 100.0
        ),
        0.0,
        100.0,
    )

    test_risk = np.where(
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

    full_scores = get_scores(
        model,
        scaler,
        avg10,
        scenario_names,
    )

    if not np.isfinite(full_scores).all():
        raise ValueError("Non-finite prediction found")

    model_artifact = {
        "model_version": "healthy-baseline-v2-avg10-scenario-aware",
        "model_type": "IsolationForest",
        "purpose": "Healthy-pattern anomaly detection for ulcer-risk indication",
        "numeric_feature_names": NUMERIC_FEATURES,
        "scenario_names": scenario_names,
        "feature_names": NUMERIC_FEATURES + [
            f"Scenario_{scenario}"
            for scenario in scenario_names
        ],
        "scaler": scaler,
        "model": model,
        "thresholds": thresholds,
        "risk_rule": {
            "Safe": "mismatch <= 10%",
            "Low Risk": "10% < mismatch <= 33.333333%",
            "Medium Risk": "33.333333% < mismatch <= 66.666667%",
            "High Risk": "mismatch > 66.666667%",
        },
        "mismatch_rule": "clip((score-q95)/(q99-q95)*100,0,100)",
        "training_type": "AVG10 only",
        "training_window_seconds": 10,
        "scenario_aware": True,
        "scenario_encoding": "one-hot",
        "dataset_logical_rows": int(len(df)),
        "avg10_rows_used": int(len(avg10)),
        "raw_rows_excluded": int((df["Type"] == "RAW").sum()),
        "split_counts": {
            "train": int(len(train)),
            "validation": int(len(validation)),
            "test": int(len(test)),
        },
        "persons": sorted(
            avg10["Person"].astype(str).unique().tolist()
        ),
        "scenarios": scenario_names,
    }

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_artifact, MODEL_FILE)

    report = {
        "status": "passed",
        "model_version": model_artifact["model_version"],
        "training_input": "AVG10 records only (10-second healthy windows)",
        "scenario_aware": True,
        "dataset": {
            "physical_lines": int(
                len(
                    DATA_FILE.read_text(
                        encoding="utf-8-sig"
                    ).splitlines()
                )
            ),
            "logical_rows_after_repair": int(len(df)),
            "avg10_rows_used": int(len(avg10)),
            "raw_rows_excluded": int(
                (df["Type"] == "RAW").sum()
            ),
            "scenarios": scenario_names,
        },
        "split": {
            "train": int(len(train)),
            "validation": int(len(validation)),
            "test": int(len(test)),
            "train_percent": float(
                len(train) / len(avg10) * 100
            ),
            "validation_percent": float(
                len(validation) / len(avg10) * 100
            ),
            "test_percent": float(
                len(test) / len(avg10) * 100
            ),
            "method": "Chronological split within each Person+Scenario group",
        },
        "validation_thresholds": thresholds,
        "test_healthy_stability": {
            "above_q95_percent": float(
                np.mean(test_scores > thresholds["q95"]) * 100
            ),
            "above_q98_percent": float(
                np.mean(test_scores > thresholds["q98"]) * 100
            ),
            "above_q99_percent": float(
                np.mean(test_scores > thresholds["q99"]) * 100
            ),
            "risk_counts": {
                label: int(np.sum(test_risk == label))
                for label in [
                    "Safe",
                    "Low Risk",
                    "Medium Risk",
                    "High Risk",
                ]
            },
        },
        "notes": [
            "AVG10 records are used because the ESP32 sends a 10-second averaged reading.",
            "Scenario is included as a one-hot feature so Walking readings are evaluated in the context of healthy Walking data.",
            "The dataset contains healthy reference data only; risk indication is not a clinical diagnosis.",
            "Mismatch percent is a healthy-pattern deviation index, not ulcer probability.",
        ],
    }

    REPORT_FILE.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("MODEL BUILD PASSED")
    print(f"Logical rows: {len(df)}")
    print(f"AVG10 rows used: {len(avg10)}")
    print(f"RAW rows excluded: {(df['Type'] == 'RAW').sum()}")
    print(
        f"Split: train={len(train)}, "
        f"validation={len(validation)}, "
        f"test={len(test)}"
    )
    print(
        "Validation thresholds:",
        json.dumps(thresholds, indent=2),
    )
    print(
        "Healthy test stability:",
        json.dumps(
            report["test_healthy_stability"],
            indent=2,
        ),
    )
    print("Model saved:", MODEL_FILE)


if __name__ == "__main__":
    main()
