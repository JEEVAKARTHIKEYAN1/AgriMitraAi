
import os
import google.generativeai as genai
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoilAgent:
    def __init__(self):
        # API Key Pool
        # You can add more keys here to distribute the load
        self.api_keys = [
            os.getenv('GOOGLE_API_KEY_1'),
            os.getenv('GOOGLE_API_KEY_2'),
            os.getenv('GOOGLE_API_KEY_3')
        ]
        # Filter out None values in case some keys are missing
        self.api_keys = [key for key in self.api_keys if key]
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
            # Standard free tier model
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
        Constructs the strict system prompt for Soil Testing Advisory.
        """
        # Context extraction
        soil_type = context_data.get('soil_type', 'Unknown')
        fertility = context_data.get('fertility', 'Unknown')
        input_params = context_data.get('input_params', {})
        
        # Format input parameters for the prompt
        params_str = ", ".join([f"{k}: {v}" for k, v in input_params.items()])
        
        prompt = f"""
You are a Soil Testing Advisory AI for Indian farming.

LANGUAGE RULE:
- Respond ONLY in clear, simple ENGLISH.

RESPONSE STYLE:
- Be concise
- Use bullet points
- Avoid over-explaining

SOIL TEST CONTEXT:
- Soil Type: {soil_type}
- Fertility Level: {fertility}
- Measured Parameters: {params_str}

YOUR TASK:
- Answer the user's question using the above soil test context.
- Provide advice on crops suitable for this soil type and fertility.
- Suggest fertilizers or soil amendments if asked or if fertility is low.
- If the question is about soil health, nutrients, or farming practices → answer it.
- If the question is unrelated to soil testing or agriculture → politely refuse.
- Do NOT repeat full soil explanations unless the user asks.

RESPONSE FORMAT:
- Give a direct answer first.
- Use bullet points if helpful.
- Ask ONE short follow-up question only if relevant.

RULES:
- No hallucinated cures or guarantees.
- Do NOT recommend banned or unsafe chemicals.
- Prefer organic / IPM methods.
- Stay strictly within the soil testing context.
"""

        return prompt

    def generate_response(self, user_message, context_data, history=[]):
        """
        Generates a response from Gemini.
        Retries with different keys on failure.
        """
        system_instruction = self.construct_system_prompt(context_data)
            
        # Combine Prompt + History + Current Message
        full_prompt = f"{system_instruction}\n\n*** CONVERSATION HISTORY ***\n"
        
        for msg in history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            full_prompt += f"{role}: {content}\n"
        
        full_prompt += f"\n*** NEW MESSAGE ***\nUser: {user_message}\nAssistant:"

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
        return f"I am unable to connect to the knowledge base at the moment. All keys exhausted. Error: {str(last_error)}"
