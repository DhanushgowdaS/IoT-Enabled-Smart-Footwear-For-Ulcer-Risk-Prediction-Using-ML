import pandas as pd

INPUT_FILE = "footwear_dataset.csv"
OUTPUT_FILE = "cleaned_footwear_dataset.csv"

REQUIRED_COLUMNS = [
    "RecordNo", "Type", "Person", "Scenario",
    "FSR1", "FSR2", "FSR3", "FSR4",
    "Temperature", "LoggedAt"
]

SENSOR_COLUMNS = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]


def main():
    print("\n=== SMART FOOTWEAR DATA CLEANING ===\n")

    df = pd.read_csv(INPUT_FILE)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print(f"Original rows: {len(df)}")

    # The AVG10 rows are the first dataset used for ML.
    df = df[df["Type"].astype(str).str.strip().str.upper() == "AVG10"].copy()
    print(f"AVG10 rows: {len(df)}")

    # Convert sensor columns to numeric.
    for col in SENSOR_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows with malformed sensor values.
    before = len(df)
    df = df.dropna(subset=SENSOR_COLUMNS)
    print(f"Removed malformed sensor rows: {before - len(df)}")

    # A temperature of 0 is used by the firmware when the DS18B20
    # is disconnected. Do not remove FSR=0 values: zero pressure can
    # be valid, especially for No_Load and unloaded sensor positions.
    before = len(df)
    df = df[df["Temperature"] != 0].copy()
    print(f"Removed disconnected-temperature rows: {before - len(df)}")

    # Keep FSR=4095. It is a valid ADC maximum in this hardware setup.
    # Keep FSR=0 as well; report it instead of treating it as automatically faulty.

    # Remove exact duplicate rows.
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed exact duplicate rows: {before - len(df)}")

    # Sort for easier inspection.
    df = df.sort_values(["Person", "Scenario", "RecordNo"]).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nCleaned rows saved: {OUTPUT_FILE}")
    print("\nSamples by Person and Scenario:")
    print(df.groupby(["Person", "Scenario"]).size().to_string())

    print("\nFSR zero counts by Scenario:")
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

    print("\nFSR=4095 counts:")
    for col in ["FSR1", "FSR2", "FSR3", "FSR4"]:
        print(f"  {col}: {(df[col] == 4095).sum()}")

    print("\nDone.")


if __name__ == "__main__":
    main()
