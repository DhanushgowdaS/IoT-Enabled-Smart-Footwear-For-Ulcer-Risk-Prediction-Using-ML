"""Validate and inspect the repaired Smart Footwear dataset before ML target design.

This script intentionally does NOT create Risk/Safe labels and does not train a model.
It reports data quality, sensor ranges, invalid placeholders, duplicates, record
sequence continuity, and AVG10 structure so the ML target can be defined from
evidence rather than from scenario names.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "Data" / "CSV" / "footwear_dataset_repaired.csv"

FEATURES = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]
FSR_COLUMNS = ["FSR1", "FSR2", "FSR3", "FSR4"]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required = [
        "RecordNo", "Type", "Person", "Scenario",
        *FEATURES, "LoggedAt"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print("=== SMART FOOTWEAR DATA VALIDATION ===")
    print(f"Input: {INPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\n--- TYPE ---")
    print(df["Type"].value_counts(dropna=False).to_string())

    print("\n--- PERSON ---")
    print(df["Person"].value_counts(dropna=False).to_string())

    print("\n--- SCENARIO (DESCRIPTIVE ONLY; NO LABELS CREATED) ---")
    print(df["Scenario"].value_counts(dropna=False).to_string())

    print("\n--- MISSING VALUES ---")
    missing_counts = df.isna().sum()
    print(missing_counts[missing_counts > 0].to_string() if missing_counts.any()
          else "No missing values detected.")

    print("\n--- DUPLICATES ---")
    print(f"Duplicate complete rows: {df.duplicated().sum()}")
    print(f"Duplicate RecordNo: {df['RecordNo'].duplicated().sum()}")

    print("\n--- FEATURE SUMMARY: ALL RECORDS ---")
    print(df[FEATURES].describe().T.to_string())

    avg = df[df["Type"].eq("AVG10")].copy()
    print(f"\n--- AVG10 RECORDS: {len(avg)} ---")
    print(avg[FEATURES].describe().T.to_string())

    print("\n--- TEMPERATURE ZERO / INVALID ---")
    print(f"Temperature == 0: {(df['Temperature'] == 0).sum()}")
    print(f"Temperature <= 0: {(df['Temperature'] <= 0).sum()}")
    if (df["Temperature"] <= 0).any():
        print("\nBy scenario:")
        print(
            df.loc[df["Temperature"] <= 0, "Scenario"]
            .value_counts()
            .to_string()
        )

    print("\n--- FSR PLACEHOLDERS / SENSOR EXTREMES ---")
    for col in FSR_COLUMNS:
        zero = df[col].eq(0).sum()
        maxed = df[col].eq(4095).sum()
        print(f"{col}: ==0 -> {zero}, ==4095 -> {maxed}")

    print("\nFSR == 0 by scenario:")
    zero_by_scenario = pd.DataFrame({
        col: df[col].eq(0).groupby(df["Scenario"]).sum()
        for col in FSR_COLUMNS
    })
    print(zero_by_scenario.to_string())

    print("\nFSR == 4095 by scenario:")
    max_by_scenario = pd.DataFrame({
        col: df[col].eq(4095).groupby(df["Scenario"]).sum()
        for col in FSR_COLUMNS
    })
    print(max_by_scenario.to_string())

    print("\n--- AVG10 EXTREMES ---")
    for col in FSR_COLUMNS:
        print(
            f"{col}: ==0 -> {avg[col].eq(0).sum()}, "
            f"==4095 -> {avg[col].eq(4095).sum()}"
        )
    print(
        f"Temperature ==0 -> {(avg['Temperature'] == 0).sum()}"
    )

    print("\n--- RECORD NUMBER SEQUENCE ---")
    record = pd.to_numeric(df["RecordNo"], errors="coerce")
    print(f"Min RecordNo: {record.min()}")
    print(f"Max RecordNo: {record.max()}")
    print(f"Unique RecordNo: {record.nunique()}")
    if record.notna().all():
        expected = set(range(int(record.min()), int(record.max()) + 1))
        actual = set(record.astype(int))
        missing_ids = sorted(expected - actual)
        print(f"Missing RecordNo values inside range: {len(missing_ids)}")
        if missing_ids:
            print(f"First missing IDs: {missing_ids[:20]}")

    print("\n--- AVG10 STRUCTURE ---")
    print("AVG10 records are expected to represent the mean of the preceding 10 raw samples.")
    print("This script does not silently alter or relabel records.")

    print("\n=== VALIDATION COMPLETE ===")


if __name__ == "__main__":
    main()
