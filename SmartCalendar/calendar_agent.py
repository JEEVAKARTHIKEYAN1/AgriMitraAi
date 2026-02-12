
import os
import google.generativeai as genai
import json
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalendarAgent:
    def __init__(self):
        # API Key Pool
        self.api_keys = [
            os.getenv('GOOGLE_API_KEY_1'),
            os.getenv('GOOGLE_API_KEY_2'),
            os.getenv('GOOGLE_API_KEY_3')
        ]
        # Filter out None values and placeholders
        self.api_keys = [
            key for key in self.api_keys 
            if key and not key.startswith('your_') and not key.startswith('PASTE_')
        ]
        
        self.current_key_index = 0
        self.model = None
        self.is_active = False
        
        if self.api_keys:
            self._configure_current_key()
        else:
            logger.warning("No valid API keys found. AI features will be disabled.")

    def _configure_current_key(self):
        """Configures Gemini with the current active key."""
        if not self.api_keys:
            logger.error("No API keys available.")
            self.is_active = False
            return

        current_key = self.api_keys[self.current_key_index]
        try:
            genai.configure(api_key=current_key)
            # Test the connection with a lightweight model or call
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.is_active = True
            logger.info(f"Switched to API Key Index: {self.current_key_index}")
        except Exception as e:
            logger.error(f"Error configuring key index {self.current_key_index}: {e}")
            self.is_active = False
            # Try next key
            self._rotate_key()

    def _rotate_key(self):
        """Rotates to the next available API key."""
        if not self.api_keys:
            return

        start_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"Rotating API Key... New Index: {self.current_key_index}")
        
        # Avoid infinite recursion if all keys fail
        if self.current_key_index != start_index:
            self._configure_current_key()
        else:
             logger.error("All API keys failed.")
             self.is_active = False

    def generate_farming_schedule(self, crop, location, planting_date):
        """
        Generates a comprehensive farming schedule for a specific crop.
        Returns a structured list of farming tasks with dates and descriptions.
        All tasks will be scheduled from today onwards (no past dates).
        """
        if not self.is_active:
            logger.error("AI Agent is not active. Cannot generate schedule.")
            return []

        # Get today's date for comparison
        today = datetime.now().date()
        planting_date_obj = datetime.strptime(planting_date, '%Y-%m-%d').date()
        
        # Calculate the earliest start date (today or planting date, whichever is later)
        earliest_date = max(today, planting_date_obj)
        
        prompt = f"""
You are an expert agricultural advisor for Indian farming.

IMPORTANT: Today's date is {today.strftime('%Y-%m-%d')}. ALL tasks must be scheduled from TODAY onwards or later. Do NOT generate any tasks with dates in the past.

TASK: Generate a detailed farming schedule for the following:
- Crop: {crop}
- Location: {location}
- Planting Date: {planting_date}
- Earliest Task Date: {earliest_date.strftime('%Y-%m-%d')} (today or planting date, whichever is later)

REQUIREMENTS:
1. If the planting date is in the future, include land preparation tasks BEFORE planting
2. If the planting date is today or in the past, start with tasks that should happen NOW (e.g., irrigation, fertilization, pest control)
3. Include specific tasks for each relevant phase:
   - Land Preparation (only if planting date is in the future)
   - Sowing/Planting (if not already done)
   - Irrigation schedule
   - Fertilizer application (with NPK details)
   - Pest and disease management
   - Weeding
   - Harvesting
4. ALL task dates must be >= {earliest_date.strftime('%Y-%m-%d')}
5. Include brief descriptions for each task

OUTPUT FORMAT (JSON):
Return ONLY a valid JSON array with this exact structure:
[
  {{
    "title": "Task name",
    "date": "YYYY-MM-DD",
    "category": "preparation|planting|irrigation|fertilization|pest_control|weeding|harvesting",
    "description": "Brief description of the task",
    "priority": "high|medium|low"
  }}
]

CRITICAL RULES:
- Return ONLY the JSON array, no additional text
- Dates must be in YYYY-MM-DD format
- ALL dates must be >= {earliest_date.strftime('%Y-%m-%d')} (NO PAST DATES!)
- Include 15-25 tasks covering the crop cycle from now onwards
- Tasks should be chronologically ordered
- Be specific to {crop} cultivation in {location}
- Adjust the schedule based on whether planting has already occurred or not
"""

        attempts = len(self.api_keys)
        last_error = None

        for _ in range(attempts):
            try:
                if not self.model:
                    self._configure_current_key()
                    if not self.is_active:
                        break
                
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                tasks = json.loads(response_text)
                
                # Filter out any tasks with past dates (safety check)
                filtered_tasks = []
                for task in tasks:
                    task_date = datetime.strptime(task['date'], '%Y-%m-%d').date()
                    if task_date >= today:
                        filtered_tasks.append(task)
                    else:
                        logger.warning(f"Filtered out past task: {task['title']} on {task['date']}")
                
                logger.info(f"Generated {len(filtered_tasks)} future tasks (filtered {len(tasks) - len(filtered_tasks)} past tasks)")
                return filtered_tasks
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Response text: {response_text}")
                last_error = e
                self._rotate_key()
            except Exception as e:
                logger.error(f"API Error with Key Index {self.current_key_index}: {e}")
                last_error = e
                self._rotate_key()

        # If all keys failed
        logger.error("All API keys exhausted.")
        return []

    def construct_chat_prompt(self, context_data):
        """
        Generates the system prompt for calendar-related queries.
        """
        crop = context_data.get('crop', 'general farming')
        location = context_data.get('location', 'India')
        current_date = context_data.get('current_date', datetime.now().strftime('%Y-%m-%d'))
        
        prompt = f"""
You are an Agricultural Calendar Expert AI for Indian farming.

LANGUAGE RULE:
- Respond ONLY in clear, simple ENGLISH.

RESPONSE STYLE:
- Be concise and practical
- Use bullet points for clarity
- Focus on actionable advice

CONTEXT:
- Crop: {crop}
- Location: {location}
- Current Date: {current_date}

YOUR TASK:
- Answer questions about farming schedules, timing, and calendar planning
- Provide advice on when to perform specific farming activities
- Suggest optimal timing for planting, fertilization, irrigation, and harvesting
- Consider seasonal factors and local climate
- If the question is unrelated to farming calendars → politely refuse

RESPONSE FORMAT:
- Give direct, actionable answers
- Use bullet points when listing steps or schedules
- Include specific timeframes when relevant
- Keep responses focused and practical

RULES:
- No hallucinated data.
- Stay within agricultural calendar context.
- Provide region-specific advice when possible.
"""
        return prompt

    def generate_response(self, user_message, context_data, history=[]):
        """
        Generates a response from Gemini based on user message, context, and history.
        """
        if not self.is_active:
             return "I'm sorry, but I cannot connect to my AI brain right now. Please check if the API keys are configured correctly."

        system_instruction = self.construct_chat_prompt(context_data)
            
        full_prompt = f"{system_instruction}\n\n"
        for msg in history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            full_prompt += f"{role}: {content}\n"
        
        full_prompt += f"User: {user_message}\nAssistant:"

        attempts = len(self.api_keys)
        last_error = None

        for _ in range(attempts):
            try:
                if not self.model:
                     self._configure_current_key()
                     if not self.is_active:
                        break
                
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.error(f"API Error with Key Index {self.current_key_index}: {e}")
                last_error = e
                self._rotate_key()

        # If all keys failed
        logger.error("All API keys exhausted.")
        return f"I am having trouble connecting to the knowledge base. All keys exhausted. Error: {str(last_error)}"
