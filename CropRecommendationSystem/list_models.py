import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# If env var is missing, fallback to the hardcoded key user provided earlier
api_key = os.getenv("GEMINI_API_KEY") or "AIzaSyDQDH8u0fL2mwoEe2P-kSs-uFvvOKW-CCI" 
genai.configure(api_key=api_key)

print(f"Using Key: {str(api_key)[:10]}...")

try:
    for model in genai.list_models():
        print(model.name)
        print("  Supported methods:", model.supported_generation_methods)
except Exception as e:
    print(f"Error: {e}")
