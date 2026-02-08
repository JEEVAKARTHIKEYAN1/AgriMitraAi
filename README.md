# AgriMitraAI 🌱

**Smart Farming Assistant** powered by Advanced AI. This integrated platform provides farmers with data-driven insights for crop selection, plant disease detection, and soil analysis.

## 🚀 Features

### 1. 🌾 Crop Recommendation
Uses Machine Learning (Random Forest) to recommend the most suitable crop based on:
- **Soil Nutrients**: N, P, K
- **Environmental Factors**: Temperature, Humidity, pH, Rainfall

### 2. 🍃 Plant Disease Detection
Leverages a **Vision Transformer (ViT)** model to instantly identify plant diseases from leaf images.
- Supports mulitple plant species.
- Provides confidence scores.
- Includes an **AI Chatbot** for disease management advice.

### 3. 🧪 Soil Testing & Analysis (NEW)
A comprehensive module for soil health assessment:
- **Input**: Soil matrix data (Nutrients + Micro-nutrients + Env).
- **Auto-Prediction**:
    - **Soil Status**: AI predicts if the soil is "High Yielding", "Balanced", or "Needs Attention".
    - **Soil Type**: AI identifies the soil texture/type (e.g., Clay, Loam, Red).
    - **Fertility Level**: Automatically determined based on the soil status.

---

## 🛠️ Tech Stack

- **Frontend**: React.js, Vite, Tailwind CSS, Framer Motion
- **Backend**: Flask (Python)
- **AI/ML**:
    - *Crop & Soil*: Scikit-Learn (Random Forest)
    - *Disease*: PyTorch, Hugging Face Transformers (ViT)
    - *Chatbot*: Google Gemini API

---

## ⚙️ Installation & Setup

### Prerequisites
- **Node.js** (v16+)
- **Python** (v3.9+)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/AgriMitraAI.git
cd AgriMitraAI
```

### 2. Backend Setup
The system uses three separate microservices:

#### Crop Recommendation System
```bash
cd CropRecommendationSystem
pip install -r requirements.txt
# Create .env file with GOOGLE_API_KEY_1, _2, _3
python api.py
# Runs on Port 5000
```

#### Plant Disease System
```bash
cd PlantDisease
pip install -r requirements.txt
# Ensure ViT model is in 'vit-plant-disease-final' folder
python app.py
# Runs on Port 5001
```

#### Soil Testing System
```bash
cd SoilTesting
pip install -r requirements.txt
python app.py
# Runs on Port 5002
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Runs on Port 5173
```

---

## 🔑 Environment Variables (.env)
Create a `.env` file in the respective backend folders with the following keys:

**CropRecommendationSystem/.env** & **PlantDisease/.env**
```env
GOOGLE_API_KEY_1=your_api_key_here
GOOGLE_API_KEY_2=your_second_key_here
GOOGLE_API_KEY_3=your_third_key_here
```

---

## 🏃‍♂️ Quick Start
To run all services at once, you can use the startup script (if available):
```powershell
python start_app.py
```
Or open 4 terminal tabs and run the services individually as shown above.

---

## 📄 License
This project is licensed under the MIT License.
