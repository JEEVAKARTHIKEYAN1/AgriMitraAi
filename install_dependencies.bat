@echo off
echo Installing AgriMitraAI Dependencies...

echo.
echo [1/3] Installing Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo [2/3] Installing Crop Recommendation System Dependencies...
cd CropRecommendationSystem
call pip install -r requirements.txt
cd ..

echo.
echo [3/3] Installing Plant Disease System Dependencies...
cd PlantDisease
call pip install -r requirements.txt
cd ..

echo.
echo All dependencies installed successfully!
pause
