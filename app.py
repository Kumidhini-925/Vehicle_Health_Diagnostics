import streamlit as st
import numpy as np
import joblib
from keras.models import load_model

# Load trained model, scaler, and feature list
model = load_model("vehicle_health_autoencoder.keras")
scaler = joblib.load("scaler.pkl")
required_features = joblib.load("trained_features.pkl")

# Define important features for user input
important_features = [
    'ENGINE_COOLANT_TEMP', 'FUEL_LEVEL', 'ENGINE_LOAD', 'ENGINE_RPM',
    'SPEED', 'THROTTLE_POS', 'AIR_INTAKE_TEMP', 'FUEL_PRESSURE',
    'INTAKE_MANIFOLD_PRESSURE', 'MAF', 'SHORT_TERM_FUEL_TRIM_BANK_1',
    'TIMING_ADVANCE'
]

# Define expected ranges/hints
feature_ranges = {
    'ENGINE_COOLANT_TEMP': (70, 110),
    'FUEL_LEVEL': (0, 100),
    'ENGINE_LOAD': (0, 100),
    'ENGINE_RPM': (0, 8000),
    'SPEED': (0, 240),
    'THROTTLE_POS': (0, 100),
    'AIR_INTAKE_TEMP': (-40, 100),
    'FUEL_PRESSURE': (0, 500),
    'INTAKE_MANIFOLD_PRESSURE': (20, 250),
    'MASS_AIR_FLOW': (0, 300),
    'SHORT_TERM_FUEL_TRIM_BANK_1': (-25, 25),
    'TIMING_ADVANCE': (-10, 40)
}

# Title
st.title("🚗 Vehicle Health Anomaly Detector")

st.markdown("Enter key vehicle sensor readings below to detect anomalies using an Autoencoder.")

# User input for important features
user_inputs = {}
for feature in important_features:
    min_val, max_val = feature_ranges.get(feature, (0, 100))
    user_inputs[feature] = st.number_input(
        f"{feature} ({min_val} to {max_val})", min_value=float(min_val), max_value=float(max_val)
    )

# Predict when button is clicked
if st.button("🔍 Diagnose Vehicle Health"):
    # Prepare full input with missing features set to 0
    full_input = []
    for feature in required_features:
        if feature in user_inputs:
            full_input.append(user_inputs[feature])
        else:
            full_input.append(0.0)  # Default or mean value

    # Convert to numpy array
    input_array = np.array(full_input).reshape(1, -1)

    # Scale and predict
    input_scaled = scaler.transform(input_array)
    reconstructed = model.predict(input_scaled)
    error = np.mean(np.square(input_scaled - reconstructed))

    # Set or load threshold
    threshold = 0.05  # Replace with joblib.load("threshold.pkl") if saved

    # Show results
    st.markdown(f"### 🔁 Reconstruction Error: `{error:.4f}`")
    if error > threshold:
        st.error("⚠️ Anomaly Detected: The vehicle condition may be abnormal.")
    else:
        st.success("✅ Vehicle is Healthy: No anomalies detected.")
