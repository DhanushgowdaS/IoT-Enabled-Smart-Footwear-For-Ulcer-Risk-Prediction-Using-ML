import joblib
import pandas as pd
from pathlib import Path

# Project root is one level above this ML folder.
ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = ROOT / "model.pkl"

# These are the exact five inputs used by the current model.pkl.
test_data = pd.DataFrame({
    "FSR1": [100.5],
    "FSR2": [200.2],
    "FSR3": [150.0],
    "FSR4": [175.5],
    "Temperature": [30.1],
})

model = joblib.load(MODEL_FILE)
prediction = model.predict(test_data)

print(f"Model: {type(model).__name__}")
print(f"Features: {list(test_data.columns)}")
print(f"Prediction: {prediction[0]}")
