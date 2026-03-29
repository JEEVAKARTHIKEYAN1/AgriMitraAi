# AgriMitraAI 🌱

**Smart Farming Assistant** powered by Advanced AI. An integrated platform providing farmers with data-driven insights for crop selection, plant disease detection, soil analysis, and automated farming schedules.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

---

## 🚀 Features & Modules

### 1. 🌾 Crop Recommendation System
An ML-powered pipeline predicting the most suitable crop using environmental data:
- ** Robust Pipeline**: Uses Random Forest Classifier with robust data preprocessing, StandardScaler, and SMOTE for handling class imbalances.
- **Evaluation Artifacts**: Generates comprehensive Learning Curves, Confusion Matrices, and Feature Importance insights.
- **Fail-safe API**: Ensures high reliability even under unexpected data anomalies.
- **Context-Aware AI Chatbot**: Get personalized farming advice based on recommended crops using Google Gemini.

### 2. 🍃 Plant Disease Detection
Leverages a **Vision Transformer (ViT)** model to identify plant diseases from leaf images:
- **Advanced Training**: Implements robust Data Augmentation, Early Stopping, and Learning Rate schedulers to prevent overfitting.
- **Evaluation Suite**: Generates Classification Reports and Confusion Matrices for precise metric tracking.
- **Confidence Scoring**: Notifies users of prediction probability to prevent false positives.
- **AI Chatbot**: Contextual disease management and actionable agricultural treatment.

### 3. 🧪 Soil Testing & Analysis
Comprehensive soil health assessment ensuring accurate agricultural foundations:
- **Adaptive Inputs**: Handles missing inputs cleanly using median imputation, enabling robust analysis even with partial real-world data.
- **Dual Predictions**: 
  - **Soil Status**: High Yielding, Balanced, or Needs Attention
  - **Soil Type**: Classification into Clay, Loam, Red, etc.
- **AI Chatbot**: Immediate advice regarding fertilizer usage, crop viability, and yield improvement.

### 4. 📅 Smart Farming Calendar
An deterministic, AI-powered farming schedule orchestrator integrated directly with the other modules:
- **Deterministic AI Generation**: Gemini API with zero temperature and top_p limiting guarantees consistent, strict JSON schema output.
- **Cross-Module Integration**: Adjusts farming timelines and nutrient requirements dynamically based on Soil Fertility results from the Soil Testing module.
- **Persistent Storage**: Robust file-based JSON persistence (`tasks.json`) mapping tasks beyond temporary server memory.
- **Lifecycle Management**: Detailed phase management (Land Prep, Sowing, Fertilization, Pest Control, Harvesting) and priority tracking.
- **AI Assistant**: Conversational knowledge base restricted to Indian agricultural calendar context.

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

### AI/ML
- **Tabular Models**: Scikit-Learn (Random Forest, Ensembles, SMOTE, Pipelines)
- **Computer Vision**: PyTorch + Hugging Face Transformers (ViT)
- **LLM Engine**: Google Gemini 2.5 Flash API (Structured outputs, deterministic settings)

---

## 📋 Prerequisites

- **Node.js** (v16+)
- **Python** (v3.9+)
- **Git**
- **Google Gemini API Keys** (Multiple keys supported for intelligent agent rotation)

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/JEEVAKARTHIKEYAN1/AgriMitraAi.git
cd AgriMitraAI
```

### 2. Backend Setup

The system uses separated microservices running on defined ports.

#### Environment Configuration
Create a single `.env` file in the root directory (you can copy from `.env.example`) and add your Google Gemini API Keys:
```bash
cp .env.example .env
```

#### Install Dependencies (All Services)
```bash
pip install fastapi uvicorn python-multipart scikit-learn joblib pandas numpy torch transformers pillow google-generativeai python-dotenv imbalanced-learn matplotlib seaborn xgboost
```

#### A. Crop Recommendation System (Port 5000)
```bash
cd CropRecommendationSystem
python api.py
```

#### B. Plant Disease Detection (Port 5001)
Ensure the ViT model is in the `vit-plant-disease-final` folder.
```bash
cd PlantDisease
python app.py
```

#### C. Soil Testing System (Port 5002)
```bash
cd SoilTesting
python app.py
```

#### D. Smart Farming Calendar (Port 5004)
```bash
cd SmartCalendar
python app.py
```

---

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access at: `http://localhost:5173`

---

## 📁 Project Structure

```
AgriMitraAI/
├── CropRecommendationSystem/
│   ├── api.py                    # Fast, fail-safe API
│   ├── crop_pipeline.py          # Unified modular ML pipeline
│   ├── agri_agent.py             # Gemini chatbot agent
│   └── model bounds/artifacts    # (.pkl files, plots)
│
├── PlantDisease/
│   ├── app.py                    
│   ├── train_vit.py              # Robust model training
│   ├── evaluate_vit.py           # Evaluation script
│   └── vit-plant-disease-final/  
│
├── SoilTesting/
│   ├── app.py                    
│   ├── train.py                  # Modular training system
│   └── model artifacts           
│
├── SmartCalendar/
│   ├── app.py                    # API with disk persistence
│   ├── calendar_agent.py         # Deterministic LLM agent
│   └── data/                     # crop requirement/yield patterns
│
└── frontend/
    ├── src/
    │   ├── pages/                # React UI Pages
    │   └── App.jsx               
    └── package.json
```

---

## 🔑 API Endpoints Overview

- **Crop Recommendation (Port 5000)**: `/predict`, `/chat`
- **Plant Disease (Port 5001)**: `/predict` (Image Upload), `/chat`
- **Soil Testing (Port 5002)**: `/predict_soil` (Handles missing values), `/chat`
- **Smart Calendar (Port 5004)**: `/generate_schedule` (Integrated heavily with Soil), `/add_task`, `/tasks`, `/update_task/{task_id}`, `/delete_task/{task_id}`, `/chat`

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
