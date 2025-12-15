import torch
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import io

MODEL_DIR = r"E:/SRI PROJECT/AgriMitraAI/PlantDisease/vit-plant-disease-final"    # ← CHANGE

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = ViTForImageClassification.from_pretrained(MODEL_DIR)
processor = ViTImageProcessor.from_pretrained(MODEL_DIR)
model.to(device)
model.eval()

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    inputs = processor(image, return_tensors="pt").to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        pred_id = logits.argmax(-1).item()

    label = model.config.id2label[pred_id]

    return {"prediction": label}
