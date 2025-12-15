import streamlit as st
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the model, scaler, and label encoder
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
le = joblib.load('label_encoder.pkl')

# Streamlit interface
st.title('Crop Recommendation System')

# Input fields
N = st.number_input('Nitrogen (N)', min_value=0.0)
P = st.number_input('Phosphorus (P)', min_value=0.0)
K = st.number_input('Potassium (K)', min_value=0.0)
temperature = st.number_input('Temperature (°C)', min_value=0.0)
humidity = st.number_input('Humidity (%)', min_value=0.0)
ph = st.number_input('pH', min_value=0.0)
rainfall = st.number_input('Rainfall (mm)', min_value=0.0)

if st.button('Predict'):
    # Prepare input
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    input_scaled = scaler.transform(input_data)
    
    # Predict
    prediction = model.predict(input_scaled)[0]
    crop = le.inverse_transform([prediction])[0]
    
    # Probability/Confidence
    probs = model.predict_proba(input_scaled)[0]
    confidence = np.max(probs) * 100
    
    st.success(f'Recommended Crop: {crop}')
    st.info(f'Confidence Level: {confidence:.2f}%')
    
    # Simple explanation using feature importance
    importances = model.feature_importances_
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    importance_dict = dict(zip(features, importances))
    top_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:3]
    
    explanation = f'This crop fits best because of high importance on: '
    explanation += ', '.join([f'{feat} ({imp:.2f})' for feat, imp in top_features])
    st.info(explanation)
    
    # Visualization: Feature Importance Bar Graph
    st.subheader('Feature Importance')
    fig, ax = plt.subplots()
    pd.Series(importance_dict).plot(kind='bar', ax=ax)
    ax.set_ylabel('Importance')
    st.pyplot(fig)