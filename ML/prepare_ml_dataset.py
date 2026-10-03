"""Prepare the repaired Smart Footwear dataset for ML training.

This creates a binary experimental target from the recorded test scenarios.
The labels are scenario-derived proxies for the project's prototype; they
are NOT clinical diagnoses of diabetic foot-ulcer risk.

Only AVG10 records are used so the model learns from stabilized sensor
readings. Scenario is used only to create the target and is not included
as a model feature.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "Data" / "CSV" / "footwear_dataset_repaired.csv"
OUTPUT_FILE = ROOT / "Data" / "CSV" / "ml_training_dataset.csv"

FEATURES = ["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]

# Prototype scenario-to-target mapping based on the experiment names.
# These are engineering labels for the current dataset, not medical labels.
SCENARIO_LABELS = {
    "No_Load": "Safe",
    "Sitting": "Safe",
    "Standing": "Safe",
    "Walking": "Safe",
    "Toe_Pressure": "Risk",
    "Heel_Pressure": "Risk",
    "High_Pressure": "Risk",
    "Left_Shift": "Risk",
    "Right_Shift": "Risk",
}


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    required = ["Type", "Scenario", *FEATURES]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Use only the stabilized 10-sample averages.
    ml_df = df[df["Type"].eq("AVG10")].copy()

    ml_df["Risk"] = ml_df["Scenario"].map(SCENARIO_LABELS)
    ml_df = ml_df.dropna(subset=["Risk"]).copy()

    ml_df[FEATURES] = ml_df[FEATURES].apply(pd.to_numeric, errors="coerce")
    ml_df = ml_df.dropna(subset=FEATURES)

    output = ml_df[FEATURES + ["Risk"]]
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    print("=== ML DATASET PREPARATION ===")
    print(f"Input: {INPUT_FILE}")
    print(f"AVG10 records selected: {len(ml_df)}")
    print(f"Output: {OUTPUT_FILE}")
    print("\nTarget distribution:")
    print(output["Risk"].value_counts().to_string())
    print("\nScenario distribution used:")
    print(ml_df["Scenario"].value_counts().to_string())
    print("\nFeatures:")
    print(", ".join(FEATURES))


if __name__ == "__main__":
    main()
