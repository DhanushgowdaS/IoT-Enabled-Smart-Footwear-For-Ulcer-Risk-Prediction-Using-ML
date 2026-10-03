import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ===========================
# Load Dataset
# ===========================

df = pd.read_excel("dataset.xlsx")

# ===========================
# Create Ulcer Risk Labels
# ===========================

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

df["Ulcer_Risk"] = df["Scenario"].map(risk_map)

# ===========================
# Features
# ===========================

X = df[[
    "FSR1",
    "FSR2",
    "FSR3",
    "FSR4",
    "Temperature"
]]

# ===========================
# Labels
# ===========================

y = df["Ulcer_Risk"]

# ===========================
# Split Dataset
# ===========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ===========================
# Random Forest Model
# ===========================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# ===========================
# Prediction
# ===========================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy :", accuracy)

print("\nClassification Report\n")
print(classification_report(y_test, predictions))

# ===========================
# Save Model
# ===========================

joblib.dump(model, "ulcer_model.pkl")

print("\nModel Saved Successfully")
