
import os
import google.generativeai as genai
import json
import logging
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

# Load environment variables from the project root .env file
load_dotenv(find_dotenv())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generation config — deterministic output
GENERATION_CONFIG = {
    "temperature": 0,
    "top_p": 1,
}

MAX_RETRIES = 2
MIN_TASKS = 10

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
        """Configures Gemini with the current active key and deterministic generation config."""
        if not self.api_keys:
            logger.error("No API keys available.")
            self.is_active = False
            return

        current_key = self.api_keys[self.current_key_index]
        try:
            genai.configure(api_key=current_key)
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config=GENERATION_CONFIG
            )
            self.is_active = True
            logger.info(f"Switched to API Key Index: {self.current_key_index}")
        except Exception as e:
            logger.error(f"Error configuring key index {self.current_key_index}: {e}")
            self.is_active = False
            self._rotate_key()

    def _rotate_key(self):
        """Rotates to the next available API key. Only called on API-level errors."""
        if not self.api_keys:
            return

        start_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"Rotating API Key... New Index: {self.current_key_index}")

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

    def get_allowed_crops(self):
        """Returns list of known crop names from loaded data."""
        return list(self.crop_data.keys()) if self.crop_data else []

    def _validate_tasks(self, raw_tasks):
        """
        Validates parsed task list against the required schema.
        Required fields: date, task, phase
        Skips invalid entries silently but logs them.
        Returns only valid tasks.
        """
        valid = []
        today = datetime.now().date()

        for i, t in enumerate(raw_tasks):
            # Required field check
            if not all(k in t for k in ('date', 'task', 'phase')):
                logger.warning(f"Task at index {i} missing required fields, skipping: {t}")
                continue
            # Date validity check
            try:
                task_date = datetime.strptime(t['date'], '%Y-%m-%d').date()
                if task_date < today:
                    logger.warning(f"Filtered past task: '{t['task']}' on {t['date']}")
                    continue
            except (ValueError, TypeError):
                logger.warning(f"Task at index {i} has invalid date format: {t.get('date')}, skipping.")
                continue
            # Normalize priority
            if t.get('priority') not in ('high', 'medium', 'low'):
                t['priority'] = 'medium'
            valid.append(t)

        return valid

    def _build_schedule_prompt(self, crop, location, planting_date, soil_fertility, target_crop_id):
        """Constructs the deterministic, structured prompt for schedule generation."""
        today = datetime.now().date()
        planting_date_obj = datetime.strptime(planting_date, '%Y-%m-%d').date()
        earliest_date = max(today, planting_date_obj)

        crop_context = ""
        if crop.lower() in self.crop_data:
            crop_context = f"\nCROP-SPECIFIC REQUIREMENTS (Ground Truth):\n{json.dumps(self.crop_data[crop.lower()], indent=2)}"

        regional_context = ""
        if location in self.yield_patterns and crop in self.yield_patterns.get(location, {}):
            regional_context = f"\nREGIONAL YIELD PATTERNS ({location}):\n{json.dumps(self.yield_patterns[location][crop], indent=2)}"

        prompt = f"""You are an agricultural scheduling system. Generate a structured farming task schedule.

INPUTS:
- Crop: {crop}
- Location: {location}
- Soil Fertility: {soil_fertility}
- Planting Date: {planting_date}
- Crop ID: {target_crop_id}
- Today's Date: {today.strftime('%Y-%m-%d')}
- Earliest Task Date: {earliest_date.strftime('%Y-%m-%d')}
{crop_context}
{regional_context}

RULES:
1. All task dates must be >= {earliest_date.strftime('%Y-%m-%d')}. Do NOT generate past dates.
2. If planting date is in the past, start from the current crop lifecycle stage.
3. Adjust fertilization recommendations based on Soil Fertility level:
   - Low fertility: increase NPK dosage recommendations
   - High fertility: reduce base NPK dosage
4. Generate 15 to 20 tasks covering: Land Preparation, Sowing, Irrigation, Fertilization, Pest Control, Weeding, Harvest.
5. Distribute tasks chronologically across the full crop lifecycle.

OUTPUT FORMAT:
Return ONLY a valid JSON array. No markdown. No explanations. No text before or after the array.
Each element must follow this exact schema:
{{
  "date": "YYYY-MM-DD",
  "task": "Descriptive task name",
  "phase": "Land Preparation|Sowing|Irrigation|Fertilization|Pest Control|Weeding|Harvest",
  "priority": "high|medium|low"
}}"""
        return prompt

    def generate_farming_schedule(self, crop, location, planting_date, soil_fertility="Unknown", crop_id=None):
        """
        Generates a deterministic farming schedule for a specific crop.
        Retries up to MAX_RETRIES times on parse failure or insufficient tasks.
        Does NOT rotate API key on JSON parse failure.
        """
        if not self.is_active:
            logger.error("AI Agent is not active. Cannot generate schedule.")
            return []

        try:
            datetime.strptime(planting_date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid planting date format: {planting_date}")
            return []

        target_crop_id = crop_id or f"crop_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        prompt = self._build_schedule_prompt(crop, location, planting_date, soil_fertility, target_crop_id)

        for attempt in range(MAX_RETRIES):
            try:
                if not self.model:
                    self._configure_current_key()
                    if not self.is_active:
                        return []

                logger.info(f"Schedule generation attempt {attempt + 1}/{MAX_RETRIES} for '{crop}'")
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()

                # Strip markdown fences if the model ignores the no-markdown rule
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()

                # Parse JSON — do NOT rotate key if this fails
                raw_tasks = json.loads(response_text)

                if not isinstance(raw_tasks, list):
                    logger.error(f"Expected JSON array, got {type(raw_tasks)}. Retrying...")
                    continue

                # Validate task schema and filter invalid entries
                valid_tasks = self._validate_tasks(raw_tasks)

                # Enforce crop_id consistency
                for task in valid_tasks:
                    task['crop_id'] = target_crop_id
                    task['crop_name'] = crop

                if len(valid_tasks) < MIN_TASKS:
                    logger.warning(
                        f"Only {len(valid_tasks)} valid tasks generated (minimum {MIN_TASKS}). "
                        f"Attempt {attempt + 1}/{MAX_RETRIES}."
                    )
                    if attempt < MAX_RETRIES - 1:
                        continue  # Retry — same key, same prompt
                    else:
                        logger.error("Max retries reached. Returning partial results.")
                        return valid_tasks

                logger.info(f"Generated {len(valid_tasks)} valid tasks for '{crop}' (ID: {target_crop_id})")
                return valid_tasks

            except json.JSONDecodeError as e:
                # Parse failure is an OUTPUT problem, not a key problem — retry without rotating
                logger.error(f"JSON parse error on attempt {attempt + 1}: {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info("Retrying with same key...")
                    continue
                else:
                    logger.error("Max retries reached. Returning empty schedule.")
                    return []

            except Exception as e:
                # True API/connection error — rotate key, do not retry
                logger.error(f"API Error with Key Index {self.current_key_index}: {e}")
                self._rotate_key()
                return []

        return []

    def construct_chat_prompt(self, context_data):
        """Generates the system prompt for calendar-related queries."""
        crop = context_data.get('crop', 'general farming')
        location = context_data.get('location', 'India')
        current_date = context_data.get('current_date', datetime.now().strftime('%Y-%m-%d'))

        prompt = f"""You are an Agricultural Calendar Expert AI for Indian farming.

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
- If the question is unrelated to farming calendars, politely refuse

RULES:
- No hallucinated data.
- Stay within agricultural calendar context.
- Provide region-specific advice when possible.
"""
        return prompt

    def generate_response(self, user_message, context_data, history=[]):
        """Generates a response from Gemini based on user message, context, and history."""
        if not self.is_active:
            return "I'm sorry, but I cannot connect to my AI brain right now. Please check if the API keys are configured correctly."

        system_instruction = self.construct_chat_prompt(context_data)
        full_prompt = f"{system_instruction}\n\n"
        for msg in history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            full_prompt += f"{role}: {content}\n"
        full_prompt += f"User: {user_message}\nAssistant:"

        for attempt in range(MAX_RETRIES):
            try:
                if not self.model:
                    self._configure_current_key()
                    if not self.is_active:
                        break
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.error(f"API Error with Key Index {self.current_key_index}: {e}")
                self._rotate_key()

        return "I am having trouble connecting to the knowledge base. Please try again later."
