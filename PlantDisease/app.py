
import io
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import logging
import uvicorn
from plant_agent import PlantAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# CONFIG
# -----------------------------
MODEL_DIR = r"E:/SRI PROJECT/AgriMitraAI/PlantDisease/vit-plant-disease-final"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# LOAD MODEL
# -----------------------------
print("Loading ViT model...")
try:
    model = ViTForImageClassification.from_pretrained(MODEL_DIR)
    processor = ViTImageProcessor.from_pretrained(MODEL_DIR)
    model.to(device)
    model.eval()
    print("Model loaded successfully!")
    MODELS_LOADED = True
except Exception as e:
    print(f"Error loading model: {e}")
    MODELS_LOADED = False

# -----------------------------
# LABEL CLEANER FUNCTION
# -----------------------------
def clean_label(raw_label: str) -> str:
    """
    Converts labels like:
    'Tomato___Early_blight'
    into:
    'Tomato - Early Blight'
    """

    if "___" not in raw_label:
        return raw_label.replace("_", " ").strip()

    plant, disease = raw_label.split("___")

    plant = plant.replace("_", " ").strip()
    disease = disease.replace("_", " ").strip()

    # If healthy class
    if "healthy" in disease.lower():
        return f"{plant} - Healthy"

    # Capitalize formatted output
    disease = disease.title()
    plant = plant.title()

    return f"{plant} - {disease}"


# -----------------------------
# PREDICT FUNCTION
# -----------------------------
def predict_image_pil(pil_image: Image.Image) -> str:
    pil_image = pil_image.convert("RGB")

    inputs = processor(pil_image, return_tensors="pt").to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        pred_id = logits.argmax(-1).item()

    raw_label = model.config.id2label[pred_id]
    cleaned_label = clean_label(raw_label)

    return cleaned_label


# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(title="AgriMitraAI - Plant Disease")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
agent = PlantAgent()

class ChatInput(BaseModel):
    message: str
    context: dict = {}
    history: list = []

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>AgriMitraAI - Plant Disease</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #ecfccb; color: #3f6212; }
                h1 { font-size: 2.5em; }
                p { font-size: 1.2em; }
                .status { padding: 10px 20px; background-color: #d9f99d; border-radius: 5px; display: inline-block; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>🍃 Plant Disease Analysis Service</h1>
            <p>ViT Model is Loaded and API is Online (FastAPI).</p>
            <div class="status">Status: <strong>Active</strong></div>
             <p><a href="/docs">View API Documentation</a></p>
        </body>
    </html>
    """


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Accepts: multipart/form-data with key 'file'
    Returns: { 'prediction': '<disease name>' }
    """
    if not MODELS_LOADED:
        raise HTTPException(status_code=500, detail="Model not loaded")

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents))

        prediction = predict_image_pil(pil_img)

        return {
            "prediction": prediction
        }

    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(data: ChatInput):
    """
    Chat endpoint for Plant Disease Advisory.
    Input: { "message": "...", "context": {...}, "history": [...] }
    """
    if not data.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        reply = agent.generate_response(data.message, data.context, data.history)
        return {'reply': reply}
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
