from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import logging
from agri_agent import AgriAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model, scaler, and label encoder
try:
    model = joblib.load('model.pkl')
    scaler = joblib.load('scaler.pkl')
    le = joblib.load('label_encoder.pkl')
except FileNotFoundError as e:
    print(f"Error loading model files: {e}")
    # Handle the error appropriately, maybe exit or return an error state
    model = scaler = le = None

# Initialize the Agent
agent = AgriAgent() # Will attempt to load GEMINI_API_KEY from env

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head>
            <title>AgriMitraAI - Crop Recommendation</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f0fdf4; color: #166534; }
                h1 { font-size: 2.5em; }
                p { font-size: 1.2em; }
                .status { padding: 10px 20px; background-color: #dcfce7; border-radius: 5px; display: inline-block; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>🌾 Crop Recommendation Service</h1>
            <p>API is Online and Ready.</p>
            <div class="status">Status: <strong>Active</strong></div>
        </body>
    </html>
    """

@app.route('/predict', methods=['POST'])
def predict():
    if not all([model, scaler, le]):
        return jsonify({'error': 'Model files not loaded. Check server logs.'}), 500

    data = request.get_json()
    
    try:
        # Extract features from the request
        features = [
            data['N'],
            data['P'],
            data['K'],
            data['temperature'],
            data['humidity'],
            data['ph'],
            data['rainfall']
        ]
    except KeyError as e:
        return jsonify({'error': f'Missing feature in request: {e}'}), 400

    # Prepare input for the model
    input_data = np.array([features])
    input_scaled = scaler.transform(input_data)
    
    # Make prediction
    prediction_idx = model.predict(input_scaled)[0]
    crop = le.inverse_transform([prediction_idx])[0]
    
    # Get prediction probabilities
    probs = model.predict_proba(input_scaled)[0]
    confidence = np.max(probs) * 100
    
    response = {
        'recommended_crop': crop,
        'confidence': f'{confidence:.2f}%'
    }
    
    return jsonify(response)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for the AgriMitraAI Agent.
    Expects JSON:
    {
        "message": "User question",
        "context": { ... prediction data ... },
        "history": [ {"role": "user", "content": "..."}, ... ]
    }
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
        logger.error(f"Chat Endpoint Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
