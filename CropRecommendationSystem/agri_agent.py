
import os
import google.generativeai as genai
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgriAgent:
    def __init__(self):
        # API Key Pool
        # You can add more keys here to distribute the load
        self.api_keys = [
            "AIzaSyDQDH8u0fL2mwoEe2P-kSs-uFvvOKW-CCI",  # Primary Key
            "AIzaSyBwPYZVVLYv15GrD4HE0cTl84JhlbcOrt8", # Placeholder 1: REPLACE THIS
            "AIzaSyAom-eptFZbqZ99CK9JOxKRixFMfTt5dbQ"  # Placeholder 2: REPLACE THIS
        ]
        self.current_key_index = 0
        self.model = None
        self._configure_current_key()

    def _configure_current_key(self):
        """Configures Gemini with the current active key."""
        if not self.api_keys:
            logger.error("No API keys available.")
            return

        current_key = self.api_keys[self.current_key_index]
        try:
            genai.configure(api_key=current_key)
            logger.info(f"Switched to API Key Index: {self.current_key_index}")
            # Using Gemini Pro (Stable)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            logger.error(f"Error configuring key index {self.current_key_index}: {e}")

    def _rotate_key(self):
        """Rotates to the next available API key."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"Rotating API Key... New Index: {self.current_key_index}")
        self._configure_current_key()

    def construct_system_prompt(self, context_data):
        """
        Generates the system prompt merging static rules with dynamic context.
        """
        
        # Safe extraction of context variables with defaults
        crop = context_data.get('recommended_crop', 'Unknown Crop')
        confidence = context_data.get('confidence', 'Unknown %')
        # Removing '%' if present for comparison
        try:
            conf_val = float(str(confidence).replace('%', ''))
        except ValueError:
            conf_val = 0.0

        soil_n = context_data.get('N', 'N/A')
        soil_p = context_data.get('P', 'N/A')
        soil_k = context_data.get('K', 'N/A')
        ph = context_data.get('ph', 'N/A')
        rainfall = context_data.get('rainfall', 'N/A')
        temperature = context_data.get('temperature', 'N/A')
        
        confidence_warning = ""
        if conf_val < 60:
            confidence_warning = "\nWARNING: The model confidence is LOW (< 60%). You MUST advise the user to consult a local agricultural officer before taking final decisions."

        prompt = f"""
You are an Agricultural Expert AI for Indian farming advisory.

LANGUAGE RULE:
- Respond ONLY in clear, simple ENGLISH.

RESPONSE STYLE:
- Be concise
- Use bullet points
- Avoid over-explaining

PREDICTION CONTEXT:
- Crop: {crop}
- Confidence: {confidence}
- N: {soil_n}, P: {soil_p}, K: {soil_k}
- pH: {ph}
- Rainfall: {rainfall} mm
- Temperature: {temperature} °C

YOUR TASK:
- Answer the user's question using the above context.
- If the question is about cultivation, pests, fertilizer, irrigation, yield, or risks → answer it.
- If the question is unrelated to agriculture → politely refuse.
- Do NOT repeat full explanations unless the user asks for them.

RESPONSE FORMAT:
- Give a direct answer first.
- Use bullet points if helpful.
- Ask ONE short follow-up question only if relevant.

RULES:
- No hallucinated data.
- Stay within the crop context.
"""
        return prompt

    def generate_response(self, user_message, context_data, history=[]):
        """
        Generates a response from Gemini based on user message, context, and history.
        Retries with different keys on failure.
        """
        system_instruction = self.construct_system_prompt(context_data)
            
        full_prompt = f"{system_instruction}\n\n"
        for msg in history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            full_prompt += f"{role}: {content}\n"
        
        full_prompt += f"User: {user_message}\nAssistant:"

        # Try up to the number of keys available (one full rotation)
        attempts = len(self.api_keys)
        last_error = None

        for _ in range(attempts):
            try:
                if not self.model:
                     self._configure_current_key()
                
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.error(f"API Error with Key Index {self.current_key_index}: {e}")
                last_error = e
                # Rotate and retry
                self._rotate_key()

        # If all keys failed
        logger.error("All API keys exhausted.")
        return f"I am having trouble connecting to the knowledge base. All keys exhausted. Error: {str(last_error)}"
