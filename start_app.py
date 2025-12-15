import subprocess
import time
import os
import sys
import webbrowser

def run_command(command, cwd=None, title=None):
    """Runs a command in a new terminal window."""
    if os.name == 'nt':  # Windows
        cmd = f'start "{title}" /B {command}'
        print(f"Executing: {cmd} in {cwd}")
        return subprocess.Popen(cmd, shell=True, cwd=cwd)
    else: # Linux/Mac (just in case, though user is on Windows)
        # This is a basic fallback, might need adjustment for specific terminals
        return subprocess.Popen(command, shell=True, cwd=cwd)

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Paths to directories
    crop_dir = os.path.join(root_dir, 'CropRecommendationSystem')
    plant_dir = os.path.join(root_dir, 'PlantDisease')
    frontend_dir = os.path.join(root_dir, 'frontend')

    # Python executables (assuming venvs are identifying correctly from exploration)
    # CropRecommendationSystem has 'venv'
    crop_python = os.path.join(crop_dir, 'venv', 'Scripts', 'python.exe')
    if not os.path.exists(crop_python):
        print(f"Warning: venv not found at {crop_python}, using system python.")
        crop_python = sys.executable

    # PlantDisease has 'vit_env'
    plant_python = os.path.join(plant_dir, 'vit_env', 'Scripts', 'python.exe')
    if not os.path.exists(plant_python):
        # Fallback to check if it's named 'venv' or just use system python
        if os.path.exists(os.path.join(plant_dir, 'venv')):
             plant_python = os.path.join(plant_dir, 'venv', 'Scripts', 'python.exe')
        else:
            print(f"Warning: vit_env not found at {plant_python}, using system python.")
            plant_python = sys.executable

    print("Starting AgriMitraAI System...")
    print("-----------------------------")

    # 1. Start Crop Recommendation API (Port 5000)
    print("Launching Crop Recommendation API (Port 5000)...")
    run_command(f'"{crop_python}" api.py', cwd=crop_dir, title="Crop API")

    # 2. Start Plant Disease API (Port 5001)
    print("Launching Plant Disease API (Port 5001)...")
    run_command(f'"{plant_python}" app.py', cwd=plant_dir, title="Plant Disease API")

    # 3. Start Frontend (Port 5173 usually)
    print("Launching React Frontend...")
    # Using 'npm run dev' which usually runs vite
    # We use 'cmd /c' to run npm properly on Windows
    run_command('npm run dev', cwd=frontend_dir, title="Frontend")

    print("\nTarget Ports:")
    print("- Crop API: http://localhost:5000")
    print("- Plant API: http://localhost:5001")
    print("- Frontend: http://localhost:5173 (Wait for Vite to start)")

    print("\nServices are starting in the background.")
    print("Press Ctrl+C to exit this launcher (Note: Background processes may persist).")
    
    # Wait a bit then try to open the browser
    time.sleep(5)
    webbrowser.open('http://localhost:5173')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting launcher...")

if __name__ == "__main__":
    main()
