import pandas as pd
from pathlib import Path

INPUT_FILE = Path("Data/CSV/footwear_dataset_repaired.csv")
OUTPUT_FILE = Path("Data/CSV/new_ml_dataset.csv")


SCENARIO_TO_RISK = {
    "No_Load": "SAFE",
    "Sitting": "SAFE",

    "Walking": "LOW",
    "Standing": "LOW",

    "Left_Shift": "MEDIUM",
    "Right_Shift": "MEDIUM",
    "Heel_Pressure": "MEDIUM",
    "Toe_Pressure": "MEDIUM",

    "High_Pressure": "HIGH",
}


def create_features(df):
    fsr = ["FSR1", "FSR2", "FSR3", "FSR4"]

    df["Pressure_Mean"] = df[fsr].mean(axis=1)
    df["Pressure_Max"] = df[fsr].max(axis=1)
    df["Pressure_Min"] = df[fsr].min(axis=1)
    df["Pressure_Std"] = df[fsr].std(axis=1)

    df["Total_Pressure"] = df[fsr].sum(axis=1)

    df["Pressure_Range"] = (
        df["Pressure_Max"] - df["Pressure_Min"]
    )

    df["Left_Load"] = df["FSR1"] + df["FSR2"]
    df["Right_Load"] = df["FSR3"] + df["FSR4"]

    df["Left_Right_Imbalance"] = (
        abs(df["Left_Load"] - df["Right_Load"])
        / (df["Total_Pressure"] + 1e-6)
    )

    df["Max_Pressure_Ratio"] = (
        df["Pressure_Max"]
        / (df["Total_Pressure"] + 1e-6)
    )

    df["High_Load_Sensors"] = (
        (df[fsr] >= 3500).sum(axis=1)
    )

    return df


def main():
    print("Loading dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Input rows: {len(df)}")

    # Create four-class prototype target
    df["Risk"] = df["Scenario"].map(SCENARIO_TO_RISK)

    if df["Risk"].isna().any():
        unknown = df.loc[
            df["Risk"].isna(),
            "Scenario"
        ].unique()

        raise ValueError(
            f"Unknown scenarios found: {unknown}"
        )

    df = create_features(df)

    # IMPORTANT:
    # Scenario, Person, RecordNo and LoggedAt
    # are deliberately excluded from ML features.

    ml_columns = [
        "FSR1",
        "FSR2",
        "FSR3",
        "FSR4",
        "Temperature",
        "Pressure_Mean",
        "Pressure_Max",
        "Pressure_Min",
        "Pressure_Std",
        "Total_Pressure",
        "Pressure_Range",
        "Left_Load",
        "Right_Load",
        "Left_Right_Imbalance",
        "Max_Pressure_Ratio",
        "High_Load_Sensors",
        "Risk",
    ]

    output = df[ml_columns].copy()

    output.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n=== NEW ML DATASET ===")
    print(f"Rows: {len(output)}")
    print(f"Features: {len(ml_columns) - 1}")

    print("\nRisk distribution:")

    counts = output["Risk"].value_counts()
    percentages = (
        output["Risk"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )

    for risk in ["SAFE", "LOW", "MEDIUM", "HIGH"]:
        print(
            f"{risk:7s}: "
            f"{counts.get(risk, 0):4d} "
            f"({percentages.get(risk, 0):.2f}%)"
        )

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
