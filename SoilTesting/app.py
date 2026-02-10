from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import numpy as np

app = Flask(__name__)
CORS(app)

# =====================================================
# 1. LOAD ARTIFACTS
# =====================================================
BASE_DIR = r"E:\SRI PROJECT\AgriMitraAI\SoilTesting"
MODELS_LOADED = False

try:
    model_output = joblib.load(f"{BASE_DIR}\\soil_model.pkl")
    model_type = joblib.load(f"{BASE_DIR}\\type_model.pkl")
    scaler = joblib.load(f"{BASE_DIR}\\scaler.pkl")
    feature_cols = joblib.load(f"{BASE_DIR}\\model_columns.pkl")
    print("ALL Artifacts loaded successfully!")
    MODELS_LOADED = True
except Exception as e:
    print(f"Error loading artifacts: {e}")

# =====================================================
# 2. HELPER FUNCTIONS
# =====================================================
def get_fertility_from_output(output_class):
    # Logic strictly aligned with dataset: 
    # 0 -> Low
    # 1 -> Medium
    # 2 -> High
    mapping = {
        0: 'Low',
        1: 'Medium',
        2: 'High'
    }
    return mapping.get(int(output_class), "Unknown")

@app.route('/predict_soil', methods=['POST'])
def predict_soil():
    if not MODELS_LOADED:
        return jsonify({'error': 'Models not loaded. Check server logs.'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # 1. Prepare Input DataFrame
        # Ensure we only have the expected columns in the right order
        # Handle None values using (x or 0) logic
        input_data = {}
        for col in feature_cols:
            val = data.get(col)
            # If val is None or empty string, default to 0.0. otherwise float
            try:
                input_data[col] = float(val) if val is not None and val != "" else 0.0
            except ValueError:
                input_data[col] = 0.0

        input_df = pd.DataFrame([input_data])
        
        # 2. Scale Features
        # Check for NaNs
        if input_df.isnull().values.any():
             return jsonify({'error': 'Input contains NaN values'}), 400

        input_scaled = scaler.transform(input_df)
        
        # 3. Predict Output (Crop/Class)
        pred_output = model_output.predict(input_scaled)[0]
        
        # 4. Predict Soil Type
        pred_type = model_type.predict(input_scaled)[0]
        
        # 5. Determine Fertility (Derived from Output)
        fertility = get_fertility_from_output(pred_output)
        
        return jsonify({
            'prediction': int(pred_output),
            'soil_type': str(pred_type),
            'fertility': fertility
        })

    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({'error': f"Processing failed: {str(e)}"}), 500


# -----------------------------
# CHATBOT ENDPOINT
# -----------------------------
from soil_agent import SoilAgent
agent = SoilAgent()

@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat endpoint for Soil Testing Advisory.
    Input: { "message": "...", "context": {...}, "history": [...] }
    """
    data = request.get_json()
    
    user_message = data.get('message', '')
    context = data.get('context', {})
    history = data.get('history', [])
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
        
    try:
        reply = agent.generate_response(user_message, context, history)
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
