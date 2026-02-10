# AgriMitraAI 🌱

**Smart Farming Assistant** powered by Advanced AI. An integrated platform providing farmers with data-driven insights for crop selection, plant disease detection, and soil analysis.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

---

## 🚀 Features

### 1. 🌾 Crop Recommendation System
Uses Machine Learning (Random Forest) to recommend the most suitable crop based on:
- **Soil Nutrients**: Nitrogen (N), Phosphorus (P), Potassium (K)
- **Environmental Factors**: Temperature, Humidity, pH, Rainfall
- **AI Chatbot**: Get personalized farming advice powered by Google Gemini

### 2. 🍃 Plant Disease Detection
Leverages a **Vision Transformer (ViT)** model to instantly identify plant diseases from leaf images:
- Supports multiple plant species
- Provides confidence scores
- **AI Chatbot**: Receive disease management and treatment recommendations

### 3. 🧪 Soil Testing & Analysis
Comprehensive soil health assessment module:
- **Input**: 15 soil parameters (N, P, K, pH, EC, OC, S, Zn, Fe, Cu, Mn, B, Moisture, Rainfall, Temperature)
- **AI Predictions**:
  - **Soil Status**: High Yielding, Balanced, or Needs Attention
  - **Soil Type**: Clay, Loam, Red, etc.
  - **Fertility Level**: Automatically determined
- **AI Chatbot**: Get soil improvement recommendations

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React.js with Vite
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Routing**: React Router

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn (ASGI)
- **CORS**: Enabled for cross-origin requests

### AI/ML
- **Crop & Soil Models**: Scikit-Learn (Random Forest)
- **Disease Detection**: PyTorch + Hugging Face Transformers (ViT)
- **AI Chatbot**: Google Gemini 2.5 Flash API
- **API Key Rotation**: Multi-key support for reliability

---

## 📋 Prerequisites

- **Node.js** (v16+)
- **Python** (v3.9+)
- **Git**
- **Google Gemini API Keys** (3 keys recommended for rotation)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/JEEVAKARTHIKEYAN1/AgriMitraAi.git
cd AgriMitraAI
```

### 2. Backend Setup

The system uses three separate microservices, each running on a different port.

#### Install Dependencies (All Services)
```bash
pip install fastapi uvicorn python-multipart scikit-learn joblib pandas numpy torch transformers pillow google-generativeai python-dotenv
```

#### A. Crop Recommendation System (Port 5000)
```bash
cd CropRecommendationSystem
```

Create `.env` file:
```env
GOOGLE_API_KEY_1=your_first_api_key
GOOGLE_API_KEY_2=your_second_api_key
GOOGLE_API_KEY_3=your_third_api_key
```

Run the service:
```bash
python api.py
```

Access at: `http://localhost:5000`  
API Docs: `http://localhost:5000/docs`

---

#### B. Plant Disease Detection (Port 5001)
```bash
cd PlantDisease
```

Create `.env` file:
```env
GOOGLE_API_KEY_1=your_first_api_key
GOOGLE_API_KEY_2=your_second_api_key
GOOGLE_API_KEY_3=your_third_api_key
```

**Important**: Ensure the ViT model is in the `vit-plant-disease-final` folder.

Run the service:
```bash
python app.py
```

Access at: `http://localhost:5001`  
API Docs: `http://localhost:5001/docs`

---

#### C. Soil Testing System (Port 5002)
```bash
cd SoilTesting
```

Create `.env` file:
```env
GOOGLE_API_KEY_1=your_first_api_key
GOOGLE_API_KEY_2=your_second_api_key
GOOGLE_API_KEY_3=your_third_api_key
```

Run the service:
```bash
python app.py
```

Access at: `http://localhost:5002`  
API Docs: `http://localhost:5002/docs`

---

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

---

## 🏃‍♂️ Quick Start

### Running All Services

Open **4 separate terminal windows**:

**Terminal 1 - Crop Recommendation:**
```bash
cd CropRecommendationSystem
python api.py
```

**Terminal 2 - Plant Disease:**
```bash
cd PlantDisease
python app.py
```

**Terminal 3 - Soil Testing:**
```bash
cd SoilTesting
python app.py
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

## 📁 Project Structure

```
AgriMitraAI/
├── CropRecommendationSystem/
│   ├── api.py                    # FastAPI app
│   ├── agri_agent.py             # Gemini chatbot agent
│   ├── model.pkl                 # Trained ML model
│   ├── scaler.pkl                # Feature scaler
│   ├── label_encoder.pkl         # Label encoder
│   └── .env                      # API keys
│
├── PlantDisease/
│   ├── app.py                    # FastAPI app
│   ├── plant_agent.py            # Gemini chatbot agent
│   ├── vit-plant-disease-final/  # ViT model directory
│   └── .env                      # API keys
│
├── SoilTesting/
│   ├── app.py                    # FastAPI app
│   ├── soil_agent.py             # Gemini chatbot agent
│   ├── soil_model.pkl            # Soil status model
│   ├── type_model.pkl            # Soil type model
│   ├── scaler.pkl                # Feature scaler
│   └── .env                      # API keys
│
└── frontend/
    ├── src/
    │   ├── pages/                # React pages
    │   ├── components/           # Reusable components
    │   └── App.jsx               # Main app component
    └── package.json
```

---

## 🔑 API Endpoints

### Crop Recommendation (Port 5000)
- `GET /` - Service status page
- `POST /predict` - Get crop recommendation
- `POST /chat` - Chat with AI agent
- `GET /docs` - Interactive API documentation

### Plant Disease (Port 5001)
- `GET /` - Service status page
- `POST /predict` - Upload image for disease detection
- `POST /chat` - Chat with AI agent
- `GET /docs` - Interactive API documentation

### Soil Testing (Port 5002)
- `GET /` - Service status page
- `POST /predict_soil` - Analyze soil parameters
- `POST /chat` - Chat with AI agent
- `GET /docs` - Interactive API documentation

---

## 🌐 Deployment

All backend services are configured to run on `0.0.0.0` (accessible from any network interface). For production deployment:

1. Set up environment variables securely
2. Use a process manager (PM2, systemd)
3. Configure reverse proxy (Nginx)
4. Enable HTTPS
5. Set up monitoring and logging

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Jeeva Karthikeyan**  
GitHub: [@JEEVAKARTHIKEYAN1](https://github.com/JEEVAKARTHIKEYAN1)

---

## 🙏 Acknowledgments

- Google Gemini API for AI chatbot capabilities
- Hugging Face for the Vision Transformer model
- FastAPI for the modern, high-performance backend framework
