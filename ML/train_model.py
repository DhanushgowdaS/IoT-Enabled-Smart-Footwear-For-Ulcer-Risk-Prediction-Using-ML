"""Legacy/reference training script.

This script is retained for historical reference. It is NOT the training
pipeline for the current production model.pkl. Do not run it to replace
model.pkl until the current labels and training procedure are verified.
"""

import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "Data" / "Excel" / "dataset.xlsx"
OUTPUT_MODEL = ROOT / "ML" / "ulcer_model.pkl"

risk_map = {
    "No Pressure": "Safe",
    "Very Light Pressure": "Safe",
    "Normal Standing": "Low Risk",
    "Normal Walking": "Low Risk",
    "Heel Pressure": "Medium Risk",
    "Toe Pressure": "Medium Risk",
    "Left Pressure": "Medium Risk",
    "Right Pressure": "Medium Risk",
    "Full Pressure": "High Risk"
}


def main():
    df = pd.read_excel(DATASET)
    df["Ulcer_Risk"] = df["Scenario"].map(risk_map)
    df = df.dropna(subset=["Ulcer_Risk"])

    X = df[["FSR1", "FSR2", "FSR3", "FSR4", "Temperature"]]
    y = df["Ulcer_Risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print("\\nAccuracy:", accuracy_score(y_test, predictions))
    print("\\nClassification Report\\n")
    print(classification_report(y_test, predictions))

    joblib.dump(model, OUTPUT_MODEL)
    print(f"\\nLegacy model saved to: {OUTPUT_MODEL}")


if __name__ == "__main__":
    main()
