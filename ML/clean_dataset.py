import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "Data" / "CSV" / "footwear_dataset.csv"
OUTPUT_FILE = ROOT / "Data" / "CSV" / "cleaned_footwear_dataset.csv"

REQUIRED_COLUMNS = [
    "RecordNo", "Type", "Person", "Scenario",
    "FSR1", "FSR2", "FSR3", "FSR4",
    "Temperature", "LoggedAt"
]

SENSOR_COLUMNS = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]


def main():
    print("\\n=== SMART FOOTWEAR DATA CLEANING ===\\n")
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print(f"Original rows: {len(df)}")

    df = df[df["Type"].astype(str).str.strip().str.upper() == "AVG10"].copy()
    print(f"AVG10 rows: {len(df)}")

    for col in SENSOR_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.dropna(subset=SENSOR_COLUMNS)
    print(f"Removed malformed sensor rows: {before - len(df)}")

    before = len(df)
    df = df[df["Temperature"] != 0].copy()
    print(f"Removed disconnected-temperature rows: {before - len(df)}")

    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed exact duplicate rows: {before - len(df)}")

    df = df.sort_values(["Person", "Scenario", "RecordNo"]).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\\nCleaned rows saved: {OUTPUT_FILE}")
    print("\\nSamples by Person and Scenario:")
    print(df.groupby(["Person", "Scenario"]).size().to_string())

    print("\\nFSR zero counts by Scenario:")
    zero_report = []
    for scenario, group in df.groupby("Scenario"):
        zero_report.append({
            "Scenario": scenario,
            "FSR1_zero": int((group["FSR1"] == 0).sum()),
            "FSR2_zero": int((group["FSR2"] == 0).sum()),
            "FSR3_zero": int((group["FSR3"] == 0).sum()),
            "FSR4_zero": int((group["FSR4"] == 0).sum()),
        })
    print(pd.DataFrame(zero_report).to_string(index=False))

    print("\\nFSR=4095 counts:")
    for col in ["FSR1", "FSR2", "FSR3", "FSR4"]:
        print(f"  {col}: {(df[col] == 4095).sum()}")

    print("\\nDone.")


if __name__ == "__main__":
    main()
