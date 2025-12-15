import io
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from flask import Flask, request, jsonify
from flask_cors import CORS

# -----------------------------
# CONFIG
# -----------------------------
MODEL_DIR = r"E:/SRI PROJECT/AgriMitraAI/PlantDisease/vit-plant-disease-final"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# LOAD MODEL
# -----------------------------
print("Loading ViT model...")
model = ViTForImageClassification.from_pretrained(MODEL_DIR)
processor = ViTImageProcessor.from_pretrained(MODEL_DIR)
model.to(device)
model.eval()

print("Model loaded successfully!")


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
# FLASK APP
# -----------------------------
app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({"message": "Plant Disease ViT API is running"})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts: multipart/form-data with key 'file'
    Returns: { 'prediction': '<disease name>' }
    """

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Use key 'file'."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file uploaded."}), 400

    try:
        image_bytes = file.read()
        pil_img = Image.open(io.BytesIO(image_bytes))

        prediction = predict_image_pil(pil_img)

        return jsonify({
            "prediction": prediction
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# CHATBOT ENDPOINT
# -----------------------------
from plant_agent import PlantAgent
agent = PlantAgent()

@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat endpoint for Plant Disease Advisory.
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


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
