import torch
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor
import os

# -----------------------------
# CONFIG
# -----------------------------
MODEL_DIR = r"E:/SRI PROJECT/AgriMitraAI/PlantDisease/vit-plant-disease-final"   # ← Change this
TEST_IMAGE = r"E:/SRI PROJECT/AgriMitraAI/PlantDisease/data/test/Blueberry___healthy/0a8febf2-434f-4723-8fbd-9482eb1f2aec___RS_HL 5504.JPG"               # ← Change this

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

# -----------------------------
# LOAD MODEL
# -----------------------------
print("Loading model...")
model = ViTForImageClassification.from_pretrained(MODEL_DIR)
processor = ViTImageProcessor.from_pretrained(MODEL_DIR)

model.eval()
model.to(device)

# -----------------------------
# PREDICT FUNCTION
# -----------------------------
def predict_image(image_path):
    img = Image.open(image_path).convert("RGB")

    inputs = processor(img, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        pred_class_id = logits.argmax(-1).item()

    label = model.config.id2label[pred_class_id]
    return label


# -----------------------------
# RUN PREDICTION
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(TEST_IMAGE):
        print("❌ Test image not found!")
        exit()

    print("Predicting:", TEST_IMAGE)
    prediction = predict_image(TEST_IMAGE)
    print("\n✅ Predicted Class:", prediction)
