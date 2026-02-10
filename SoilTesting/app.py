
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
import uvicorn
from soil_agent import SoilAgent

app = FastAPI(title="AgriMitraAI - Soil Testing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# initialize agent
agent = SoilAgent()

# Pydantic Models for Input Validation
class SoilInput(BaseModel):
    N: float = 0.0
    P: float = 0.0
    K: float = 0.0
    pH: float = 0.0
    EC: float = 0.0
    OC: float = 0.0
    S: float = 0.0
    Zn: float = 0.0
    Fe: float = 0.0
    Cu: float = 0.0
    Mn: float = 0.0
    B: float = 0.0
    Moisture: float = 0.0
    Annual_Rainfall: float = 0.0
    Temperature: float = 0.0

class ChatInput(BaseModel):
    message: str
    context: dict = {}
    history: list = []

@app.post('/predict_soil')
async def predict_soil(data: SoilInput):
    if not MODELS_LOADED:
        raise HTTPException(status_code=500, detail="Models not loaded. Check server logs.")

    try:
        # 1. Prepare Input DataFrame
        # Ensure we only have the expected columns in the right order
        input_data = {}
        input_dict = data.dict()
        
        for col in feature_cols:
             input_data[col] = input_dict.get(col, 0.0)

        input_df = pd.DataFrame([input_data])
        
        # 2. Scale Features
        # Check for NaNs
        if input_df.isnull().values.any():
             raise HTTPException(status_code=400, detail="Input contains NaN values")

        input_scaled = scaler.transform(input_df)
        
        # 3. Predict Output (Crop/Class)
        pred_output = model_output.predict(input_scaled)[0]
        
        # 4. Predict Soil Type
        pred_type = model_type.predict(input_scaled)[0]
        
        # 5. Determine Fertility (Derived from Output)
        fertility = get_fertility_from_output(pred_output)
        
        return {
            'prediction': int(pred_output),
            'soil_type': str(pred_type),
            'fertility': fertility
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/chat")
async def chat(data: ChatInput):
    """
    Chat endpoint for Soil Testing Advisory.
    Input: { "message": "...", "context": {...}, "history": [...] }
    """
    if not data.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        reply = agent.generate_response(data.message, data.context, data.history)
        return {'reply': reply}
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5002)
