import csv
import io
import re
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

DATA_FILE = Path("Data/client2_footwear_dataset.csv")
MODEL_FILE = Path("ML/ulcer_risk_model.pkl")

FEATURES = [
    "FSR1","FSR2","FSR3","FSR4","Temperature",
    "FSR_Average","FSR_Max","FSR_Min","FSR_STD",
    "FSR1_Ratio","FSR2_Ratio","FSR3_Ratio","FSR4_Ratio"
]

def repair_csv(text):
    lines = text.splitlines()
    header = lines[0]
    repaired = [header]
    for line in lines[1:]:
        parts = re.split(r'(?<=\d)(?=\d{4,5},(?:RAW|AVG10),)', line)
        repaired.extend(parts)
    rows = list(csv.reader(io.StringIO("\n".join(repaired))))
    valid = [row for row in rows[1:] if len(row) == 10]
    if not valid:
        raise ValueError("No valid dataset records found")
    return pd.DataFrame(valid, columns=rows[0])

def make_features(df):
    fs = df[["FSR1","FSR2","FSR3","FSR4"]].to_numpy(float)
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
        ratios
    ])

text = DATA_FILE.read_text(encoding="utf-8")
df = repair_csv(text)

for column in FEATURES[:5]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df[df["Type"].eq("RAW")].dropna(subset=FEATURES[:5]).copy()

X = make_features(df)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=500,
    contamination="auto",
    random_state=42,
    n_jobs=-1
)
model.fit(X_scaled)

scores = -model.decision_function(X_scaled)
q50, q90, q95, q98, q99 = np.percentile(scores, [50, 90, 95, 98, 99])

artifact = {
    "model_type": "IsolationForest healthy-baseline anomaly detector",
    "model": model,
    "scaler": scaler,
    "feature_names": FEATURES,
    "calibration": {
        "q50": float(q50),
        "q90": float(q90),
        "q95": float(q95),
        "q98": float(q98),
        "q99": float(q99)
    },
    "training_rows": len(df),
    "persons": sorted(df["Person"].astype(str).unique().tolist()),
    "scenarios": sorted(df["Scenario"].astype(str).unique().tolist())
}

MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(artifact, MODEL_FILE)

print("Model saved:", MODEL_FILE)
print("Training rows:", len(df))
print("Persons:", artifact["persons"])
print("Scenarios:", artifact["scenarios"])
print("Calibration:", artifact["calibration"])
