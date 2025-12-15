# AgriMitraAI

Integrated Agricultural Smart Assistant combining Crop Recommendation and Plant Disease Detection.

## Project Structure

- **CropRecommendationSystem**: Flask backend for crop suggestions.
- **PlantDisease**: Flask backend for disease detection (ViT model).
- **frontend**: React + Vite frontend application.

## Prerequisites

- Node.js installed.
- Python installed.
- Required Python packages installed in respective virtual environments.

## How to Run

The easiest way to run the entire system is using the provided startup script.

### 1. Run the Startup Script

```powershell
python start_app.py
```

This script will:
1. Start the Crop Recommendation API on port `5000`.
2. Start the Plant Disease API on port `5001`.
3. Start the React Frontend (usually on port `5173`).
4. Automatically open your default browser to the frontend.

### Manual Startup

If you prefer to start services individually:

**Terminal 1 (Crop API):**
```bash
cd CropRecommendationSystem
./venv/Scripts/activate
python api.py
```

**Terminal 2 (Plant API):**
```bash
cd PlantDisease
./vit_env/Scripts/activate
python app.py
```

**Terminal 3 (Frontend):**
```bash
cd frontend
npm run dev
```

## Usage

1. **Crop Recommendation**: Go to the "Crop Recommendation" tab, enter soil details, and get a prediction.
2. **Plant Disease**: Go to the "Plant Disease" tab, upload a leaf image, and get a diagnosis.
