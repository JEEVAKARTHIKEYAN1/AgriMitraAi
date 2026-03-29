
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
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
    scaler = joblib.load(f"{BASE_DIR}\\scaler.pkl")
    feature_cols = joblib.load(f"{BASE_DIR}\\model_columns.pkl")
    medians = joblib.load(f"{BASE_DIR}\\medians.pkl")
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
    N: Optional[float] = None
    P: Optional[float] = None
    K: Optional[float] = None
    pH: Optional[float] = None
    EC: Optional[float] = None
    OC: Optional[float] = None
    S: Optional[float] = None
    Zn: Optional[float] = None
    Fe: Optional[float] = None
    Cu: Optional[float] = None
    Mn: Optional[float] = None
    B: Optional[float] = None
    Moisture: Optional[float] = None
    soil_type: str = "Unknown"

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
        input_data = {}
        input_dict = data.dict()
        
        for col in feature_cols:
             val = input_dict.get(col)
             if val is None:
                 val = medians.get(col, 0.0)
             input_data[col] = val

        input_df = pd.DataFrame([input_data])
        
        # 2. Scale Features
        input_scaled = scaler.transform(input_df)
        
        # 3. Predict Output (Fertility)
        pred_output = model_output.predict(input_scaled)[0]
        
        # 4. Determine Fertility (Derived from Output)
        fertility = get_fertility_from_output(pred_output)
        
        return {
            'prediction': int(pred_output),
            'soil_type': data.soil_type,
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
