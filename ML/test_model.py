import joblib
import pandas as pd

# Load your saved model
model = joblib.load('model.pkl')

# Replace these column names with the exact features your model expects
# Examples: 'pressure_sensor_1', 'pressure_sensor_2', 'temp_sensor'
test_data = pd.DataFrame({
    'feature_1': [100.5], 
    'feature_2': [200.2],
    'feature_3': [30.1]
})

# Get the prediction
prediction = model.predict(test_data)

# Print the result
print(f"Prediction result: {prediction}")
