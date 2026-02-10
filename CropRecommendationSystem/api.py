
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import joblib
import numpy as np
import logging
import uvicorn
from agri_agent import AgriAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AgriMitraAI - Crop Recommendation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model, scaler, and label encoder
try:
    model = joblib.load('model.pkl')
    scaler = joblib.load('scaler.pkl')
    le = joblib.load('label_encoder.pkl')
    MODELS_LOADED = True
except FileNotFoundError as e:
    logger.error(f"Error loading model files: {e}")
    MODELS_LOADED = False
    model = scaler = le = None

# Initialize the Agent
agent = AgriAgent()

# Pydantic Models for Input Validation
class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class ChatInput(BaseModel):
    message: str
    context: dict = {}
    history: list = []

@app.get("/", response_class=HTMLResponse)
async def home():
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
            <p>Fail-safe API is Online and Ready (FastAPI).</p>
            <div class="status">Status: <strong>Active</strong></div>
            <p><a href="/docs">View API Documentation</a></p>
        </body>
    </html>
    """

@app.post("/predict")
async def predict(data: CropInput):
    if not MODELS_LOADED:
        raise HTTPException(status_code=500, detail="Model files not loaded. Check server logs.")

    try:
        # Extract features from the pydantic model
        features = [
            data.N,
            data.P,
            data.K,
            data.temperature,
            data.humidity,
            data.ph,
            data.rainfall
        ]
        
        # Prepare input for the model
        input_data = np.array([features])
        input_scaled = scaler.transform(input_data)
        
        # Make prediction
        prediction_idx = model.predict(input_scaled)[0]
        crop = le.inverse_transform([prediction_idx])[0]
        
        # Get prediction probabilities
        probs = model.predict_proba(input_scaled)[0]
        confidence = np.max(probs) * 100
        
        return {
            'recommended_crop': crop,
            'confidence': f'{confidence:.2f}%'
        }
        
    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(data: ChatInput):
    """
    Chat endpoint for the AgriMitraAI Agent.
    """
    if not data.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        reply = agent.generate_response(data.message, data.context, data.history)
        return {'reply': reply}
    except Exception as e:
        logger.error(f"Chat Endpoint Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
