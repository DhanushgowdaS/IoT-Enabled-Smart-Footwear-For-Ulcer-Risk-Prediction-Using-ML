"""Inspect RecordNo integrity without modifying the dataset.

This diagnostic is intentionally non-destructive. It looks for unusually large
RecordNo jumps and values that may contain concatenated record numbers after
CSV newline corruption. It does not repair, relabel, or drop any records.
"""

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "Data" / "CSV" / "footwear_dataset_repaired.csv"


def split_concatenated_record(value: int):
    text = str(value)
    candidates = []
    for width in (3, 4, 5, 6):
        if len(text) > width:
            left = int(text[:width])
            right = int(text[width:])
            if right > 0:
                candidates.append((left, right))
    return candidates


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    record = pd.to_numeric(df["RecordNo"], errors="coerce")

    print("=== RECORD NUMBER INTEGRITY INSPECTION ===")
    print(f"Input: {INPUT_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Non-numeric RecordNo: {record.isna().sum()}")

    if record.isna().any():
        print("\nRows with non-numeric RecordNo:")
        print(df.loc[record.isna(), ["RecordNo", "Type", "LoggedAt"]].to_string(index=False))
        return

    values = record.astype("int64")
    diffs = values.diff()

    print("\n--- BASIC SEQUENCE ---")
    print(f"Minimum: {values.min()}")
    print(f"Maximum: {values.max()}")
    print(f"Unique: {values.nunique()}")
    print(f"Positive jumps > 1: {(diffs > 1).sum()}")
    print(f"Backward jumps: {(diffs < 0).sum()}")

    suspicious = df.loc[
        diffs.gt(1) | diffs.lt(0),
        ["RecordNo", "Type", "Person", "Scenario", "LoggedAt"]
    ].copy()
    suspicious.insert(0, "PreviousRecordNo", values.shift().loc[suspicious.index])

    print("\n--- SUSPICIOUS SEQUENCE BREAKS ---")
    if suspicious.empty:
        print("No sequence breaks detected.")
    else:
        print(suspicious.head(100).to_string(index=False))

    print("\n--- POSSIBLE CONCATENATED RECORD NUMBERS ---")
    found = []
    for idx, value in values.items():
        candidates = split_concatenated_record(int(value))
        for left, right in candidates:
            if right == left + 1:
                found.append((idx, int(value), left, right))
                break

    if not found:
        print("No obvious concatenation pattern detected.")
    else:
        print(f"Candidates found: {len(found)}")
        for idx, value, left, right in found[:100]:
            row = df.loc[idx]
            print(
                f"row={idx}, RecordNo={value}, possible={left}+{right}, "
                f"Type={row['Type']}, LoggedAt={row['LoggedAt']}"
            )

    print("\n--- RECORDNO VS DATA ORDER ---")
    print(
        "RecordNo is treated as metadata only. This diagnostic does not use it "
        "as an ML feature and does not alter the dataset."
    )

    print("\n=== INSPECTION COMPLETE ===")


if __name__ == "__main__":
    main()
