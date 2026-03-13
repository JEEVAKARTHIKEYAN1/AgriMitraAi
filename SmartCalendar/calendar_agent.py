
import os
import google.generativeai as genai
import json
import logging
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta

# Load environment variables from the project root .env file
load_dotenv(find_dotenv())

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
        
        # Load Crop Requirements Data
        self.crop_data = {}
        self.yield_patterns = {}
        self._load_crop_data()
        
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

    def _load_crop_data(self):
        """Loads crop requirements from the JSON file."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(current_dir, "data", "crop_requirements.json")
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.crop_data = json.load(f)
                logger.info(f"Loaded requirements for {len(self.crop_data)} crops.")
            else:
                logger.warning("crop_requirements.json not found.")
                
            yield_data_file = os.path.join(current_dir, "data", "crop_yield_patterns.json")
            if os.path.exists(yield_data_file):
                with open(yield_data_file, 'r') as f:
                    self.yield_patterns = json.load(f)
                logger.info(f"Loaded yield patterns for {len(self.yield_patterns)} states.")
            else:
                logger.warning("crop_yield_patterns.json not found.")
                
        except Exception as e:
            logger.error(f"Error loading crop/yield data: {e}")

    def generate_farming_schedule(self, crop, location, planting_date, crop_id=None):
        """
        Generates a comprehensive farming schedule for a specific crop.
        This follows the Smart Calendar Orchestrator logic.
        """
        if not self.is_active:
            logger.error("AI Agent is not active. Cannot generate schedule.")
            return []

        # Get today's date for comparison
        today = datetime.now().date()
        try:
            planting_date_obj = datetime.strptime(planting_date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid planting date format: {planting_date}")
            return []
        
        # Calculate the earliest start date (today or planting date, whichever is later)
        earliest_date = max(today, planting_date_obj)
        
        # Use a default crop_id if none provided
        target_crop_id = crop_id or f"crop_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        prompt = f"""
You are the Smart Calendar Orchestrator for AgriMitraAI.
Your job is to generate a professional, independent farming schedule for a specific crop cycle.

SYSTEM OBJECTIVE:
Generate a full lifecycle plan for:
- Crop: {crop}
- Location: {location}
- Planting Date: {planting_date}
- Crop ID: {target_crop_id}

{f"CROP-SPECIFIC DATA (Ground Truth): {json.dumps(self.crop_data.get(crop.lower(), {}), indent=2)}" if crop.lower() in self.crop_data else ""}
{f"REGIONAL HISTORICAL PATTERNS ({location}): {json.dumps(self.yield_patterns.get(location, {}).get(crop, {}), indent=2)}" if location in self.yield_patterns and crop in self.yield_patterns.get(location, {}) else ""}

CORE RULES:
1. DATE VALIDATION:
- Today's date is {today.strftime('%Y-%m-%d')}. 
- Do NOT generate past tasks.
- If the planting date ({planting_date}) is in the past, skip land preparation and start from the current lifecycle stage.
- All tasks must be >= {earliest_date.strftime('%Y-%m-%d')}.

2. SCHEDULE STRUCTURE:
Generate a plan covering:
- Land Preparation (if applicable)
- Sowing / Transplanting
- Irrigation Schedule
- Fertilization (with NPK details based on ground truth)
- Pest & Disease Monitoring
- Harvesting

3. OUTPUT FORMAT (JSON):
Return ONLY a valid JSON array. Each task must follow this exact schema:
{{
  "task_id": "unique_string",
  "crop_id": "{target_crop_id}",
  "crop_name": "{crop}",
  "phase": "Land Preparation|Sowing|Irrigation|Fertilization|Pest Control|Harvest",
  "title": "Task name",
  "description": "Professional description with data-driven advice",
  "date": "YYYY-MM-DD",
  "category": "preparation|planting|irrigation|fertilization|pest_control|weeding|harvesting",
  "priority": "high|medium|low",
  "status": "pending"
}}

CRITICAL:
- Return ONLY the JSON array. No explanations. No markdown.
- Include 15-25 tasks chronologically.
- Ensure NPK values in descriptions align with Ground Truth data if provided.
- Ensure season/yield expectations align with Regional Patterns if provided.
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
                
                # Extract JSON from response (handle markdown code blocks if the AI ignores "no markdown" rule)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                tasks = json.loads(response_text)
                
                # Filter out any tasks with past dates (safety check)
                filtered_tasks = []
                for task in tasks:
                    try:
                        task_date = datetime.strptime(task['date'], '%Y-%m-%d').date()
                        if task_date >= today:
                            # Ensure crop_id and crop_name are consistent
                            task['crop_id'] = target_crop_id
                            task['crop_name'] = crop
                            filtered_tasks.append(task)
                        else:
                            logger.warning(f"Filtered out past task: {task.get('title')} on {task.get('date')}")
                    except (ValueError, KeyError):
                        continue
                
                logger.info(f"Generated {len(filtered_tasks)} tasks for {crop} (ID: {target_crop_id})")
                return filtered_tasks
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
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
