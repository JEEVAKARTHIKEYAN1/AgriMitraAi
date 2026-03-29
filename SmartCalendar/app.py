
import os
import json
import uuid
import logging
import uvicorn

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime, date

from calendar_agent import CalendarAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AgriMitraAI - Smart Farming Calendar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Calendar Agent
agent = CalendarAgent()

# ─── File-Based Persistence ────────────────────────────────────────────────────

TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

def _load_tasks() -> list:
    """Load tasks from tasks.json on startup. Returns empty list if file missing or corrupt."""
    if not os.path.exists(TASKS_FILE):
        logger.info("tasks.json not found. Starting with empty task list.")
        return []
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                logger.info(f"Loaded {len(data)} tasks from tasks.json")
                return data
            logger.warning("tasks.json did not contain a list. Starting fresh.")
            return []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load tasks.json: {e}. Starting with empty task list.")
        return []

def _save_tasks(tasks: list):
    """Persist current task list to tasks.json atomically."""
    try:
        tmp_file = TASKS_FILE + ".tmp"
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, TASKS_FILE)
    except IOError as e:
        logger.error(f"Failed to save tasks.json: {e}")

# Load tasks on startup
tasks_db: list = _load_tasks()

# ─── Pydantic Models ───────────────────────────────────────────────────────────

class ScheduleInput(BaseModel):
    crop: str
    soil_fertility: str = "Unknown"   # Integration point: from Soil Testing module
    location: str
    planting_date: str                # Format: YYYY-MM-DD

class TaskInput(BaseModel):
    title: str
    date: str
    category: str
    description: Optional[str] = ""
    priority: Optional[str] = "medium"
    crop_id: Optional[str] = "manual"
    crop_name: Optional[str] = "Custom"
    phase: Optional[str] = "Maintenance"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
    status: Optional[str] = None   # pending | completed | updated | deleted
    phase: Optional[str] = None

class ChatInput(BaseModel):
    message: str
    context: dict = {}
    history: list = []

# ─── Input Validation Helpers ──────────────────────────────────────────────────

def _validate_schedule_input(data: ScheduleInput):
    """
    Validates schedule generation inputs.
    Raises HTTPException with descriptive messages on failure.
    """
    # Crop: must be non-empty
    crop_clean = data.crop.strip()
    if not crop_clean:
        raise HTTPException(status_code=400, detail="'crop' must be a non-empty string.")

    # Crop: check against known crops if data is loaded
    allowed_crops = agent.get_allowed_crops()
    if allowed_crops and crop_clean.lower() not in allowed_crops:
        raise HTTPException(
            status_code=400,
            detail=f"Crop '{crop_clean}' is not in the known crop list. "
                   f"Supported crops: {', '.join(sorted(allowed_crops))}."
        )

    # Location: must be non-empty
    if not data.location.strip():
        raise HTTPException(status_code=400, detail="'location' must be a non-empty string.")

    # Soil fertility: must be non-empty
    if not data.soil_fertility.strip():
        raise HTTPException(status_code=400, detail="'soil_fertility' must be a non-empty string.")

    # Planting date: valid format
    try:
        planting_date_obj = datetime.strptime(data.planting_date, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid 'planting_date' format. Use YYYY-MM-DD.")

    # Planting date: must not be more than 1 year in the past (allow current lifecycle scheduling)
    today = date.today()
    days_past = (today - planting_date_obj).days
    if days_past > 365:
        raise HTTPException(
            status_code=400,
            detail="'planting_date' is more than 1 year in the past. Please provide a valid planting date."
        )

# ─── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    ai_status = "Active" if agent.is_active else "Inactive (Check API Keys)"
    status_color = "#dcfce7" if agent.is_active else "#fee2e2"

    return f"""
    <html>
        <head>
            <title>AgriMitraAI - Smart Farming Calendar</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                p {{ font-size: 1.2em; }}
                .status {{ padding: 10px 20px; background-color: rgba(255,255,255,0.2); border-radius: 5px; display: inline-block; margin-top: 20px; }}
                a {{ color: #ffd700; text-decoration: none; font-weight: bold; }}
                a:hover {{ text-decoration: underline; }}
                .ai-status {{ margin-top: 10px; font-weight: bold; color: {status_color}; text-shadow: 1px 1px 2px black; }}
            </style>
        </head>
        <body>
            <h1>📅 Smart Farming Calendar Service</h1>
            <p>AI-Powered Farming Schedule &amp; Task Management (FastAPI).</p>
            <div class="status">Status: <strong>Active</strong></div>
            <div class="ai-status">AI Agent: {ai_status}</div>
            <p>Tasks persisted to: <code>tasks.json</code></p>
            <p><a href="/docs">View API Documentation</a></p>
        </body>
    </html>
    """

@app.get("/ai_status")
async def get_ai_status():
    """Check if the AI agent is active and fully configured."""
    return {
        "status": "active" if agent.is_active else "inactive",
        "message": "AI is ready" if agent.is_active else "AI is disabled. Please check API keys in .env file."
    }

@app.post("/generate_schedule")
async def generate_schedule(data: ScheduleInput):
    """
    Generate an AI-powered farming schedule for a specific crop.

    Accepts soil_fertility from the Soil Testing module output.
    Uses crop data from the Crop Recommendation module's dataset.
    All generated tasks are persisted to tasks.json.
    """
    if not agent.is_active:
        raise HTTPException(
            status_code=503,
            detail="AI service is currently unavailable. Please check server logs/keys."
        )

    # Strict input validation
    _validate_schedule_input(data)

    crop_clean = data.crop.strip()
    location_clean = data.location.strip()
    fertility_clean = data.soil_fertility.strip()

    try:
        logger.info(
            f"Generating schedule | crop={crop_clean} | location={location_clean} | "
            f"soil_fertility={fertility_clean} | planting_date={data.planting_date}"
        )

        crop_id = f"crop_{uuid.uuid4().hex[:8]}"

        # Generate schedule — agent handles retry logic internally
        tasks = agent.generate_farming_schedule(
            crop=crop_clean,
            location=location_clean,
            planting_date=data.planting_date,
            soil_fertility=fertility_clean,
            crop_id=crop_id
        )

        if not tasks:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate a valid schedule. Please try again."
            )

        # Map agent output schema → storage schema (task → title, add metadata)
        new_tasks = []
        for t in tasks:
            task_entry = {
                'id': str(uuid.uuid4()),
                'task_id': t.get('task_id', f"t_{uuid.uuid4().hex[:6]}"),
                'crop_id': crop_id,
                'crop_name': crop_clean,
                'phase': t.get('phase', 'General'),
                'title': t.get('task', t.get('title', 'Untitled Task')),   # new schema: 'task' field
                'date': t.get('date', data.planting_date),
                'category': _phase_to_category(t.get('phase', '')),
                'description': t.get('description', ''),
                'priority': t.get('priority', 'medium'),
                'status': 'pending',
                'completed': False,
                'location': location_clean,
                'soil_fertility': fertility_clean,
            }
            tasks_db.append(task_entry)
            new_tasks.append(task_entry)

        # Persist to disk
        _save_tasks(tasks_db)

        return {
            'message': f'Successfully generated {len(new_tasks)} tasks for {crop_clean}',
            'crop_id': crop_id,
            'tasks': new_tasks,
            'crop': crop_clean,
            'location': location_clean,
            'soil_fertility': fertility_clean,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schedule Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _phase_to_category(phase: str) -> str:
    """Maps phase name to category slug for frontend color-coding."""
    mapping = {
        "Land Preparation": "preparation",
        "Sowing": "planting",
        "Irrigation": "irrigation",
        "Fertilization": "fertilization",
        "Pest Control": "pest_control",
        "Weeding": "weeding",
        "Harvest": "harvesting",
    }
    return mapping.get(phase, "general")

@app.post("/add_task")
async def add_task(data: TaskInput):
    """Add a custom farming task to the calendar."""
    try:
        try:
            datetime.strptime(data.date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        if not data.title.strip():
            raise HTTPException(status_code=400, detail="Task title must not be empty.")

        task_entry = {
            'id': str(uuid.uuid4()),
            'task_id': f"manual_{uuid.uuid4().hex[:6]}",
            'crop_id': data.crop_id,
            'crop_name': data.crop_name,
            'phase': data.phase,
            'title': data.title,
            'date': data.date,
            'category': data.category,
            'description': data.description,
            'priority': data.priority,
            'status': 'pending',
            'completed': False,
            'soil_fertility': 'N/A',
        }

        tasks_db.append(task_entry)
        _save_tasks(tasks_db)
        logger.info(f"Added task: {data.title} on {data.date}")

        return {
            'message': 'Task added successfully',
            'task': task_entry
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add Task Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Retrieve tasks for a specific date range.
    If no dates provided, returns all tasks.
    """
    try:
        filtered_tasks = tasks_db

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                filtered_tasks = [t for t in filtered_tasks if datetime.strptime(t['date'], '%Y-%m-%d') >= start]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                filtered_tasks = [t for t in filtered_tasks if datetime.strptime(t['date'], '%Y-%m-%d') <= end]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        filtered_tasks = sorted(filtered_tasks, key=lambda x: x['date'])

        return {
            'count': len(filtered_tasks),
            'tasks': filtered_tasks
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get Tasks Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update_task/{task_id}")
async def update_task(task_id: str, data: TaskUpdate):
    """Update a task's details with strict consistency rules."""
    try:
        task = next((t for t in tasks_db if t['id'] == task_id), None)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        today = date.today().strftime('%Y-%m-%d')

        if data.title is not None:
            if not data.title.strip():
                raise HTTPException(status_code=400, detail="Task title must not be empty.")
            task['title'] = data.title
        if data.date is not None:
            if data.date < today:
                raise HTTPException(status_code=400, detail="Cannot set task date in the past.")
            task['date'] = data.date
        if data.category is not None:
            task['category'] = data.category
        if data.description is not None:
            task['description'] = data.description
        if data.priority is not None:
            if data.priority not in ('high', 'medium', 'low'):
                raise HTTPException(status_code=400, detail="Priority must be 'high', 'medium', or 'low'.")
            task['priority'] = data.priority
        if data.completed is not None:
            task['completed'] = data.completed
            task['status'] = 'completed' if data.completed else 'pending'
        if data.phase is not None:
            task['phase'] = data.phase
        if data.status is not None:
            task['status'] = data.status
        elif data.completed is None:
            task['status'] = 'updated'

        _save_tasks(tasks_db)
        logger.info(f"Updated task {task_id} for crop '{task.get('crop_name')}'")

        return {
            'message': 'Task updated successfully',
            'task': task
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update Task Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task with lifecycle awareness."""
    try:
        task = next((t for t in tasks_db if t['id'] == task_id), None)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        critical_tasks = ['sowing', 'planting', 'transplanting']
        is_critical = (
            task.get('category', '').lower() in critical_tasks or
            'sow' in task.get('title', '').lower()
        )

        tasks_db.remove(task)
        _save_tasks(tasks_db)
        logger.info(f"Deleted task {task_id} ('{task.get('title')}')")

        return {
            'message': 'Task deleted successfully',
            'task_id': task_id,
            'is_critical': is_critical,
            'crop_id': task.get('crop_id'),
            'warning': "Critical task deleted. Crop lifecycle may be inconsistent." if is_critical else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete Task Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_crop/{crop_id}")
async def delete_crop(crop_id: str):
    """Delete all tasks associated with a specific crop ID."""
    try:
        global tasks_db
        initial_count = len(tasks_db)
        tasks_db = [t for t in tasks_db if t.get('crop_id') != crop_id]
        deleted_count = initial_count - len(tasks_db)

        _save_tasks(tasks_db)
        logger.info(f"Deleted crop {crop_id}: {deleted_count} tasks removed")

        return {
            'message': f'Successfully deleted crop cycle and {deleted_count} tasks',
            'crop_id': crop_id,
            'deleted_tasks': deleted_count
        }
    except Exception as e:
        logger.error(f"Delete Crop Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/rename_crop/{crop_id}")
async def rename_crop(crop_id: str, new_name: str):
    """Rename all occurrences of a crop name for a specific crop ID."""
    try:
        if not new_name.strip():
            raise HTTPException(status_code=400, detail="New name must not be empty.")

        updated_count = 0
        for task in tasks_db:
            if task.get('crop_id') == crop_id:
                task['crop_name'] = new_name.strip()
                updated_count += 1

        _save_tasks(tasks_db)
        logger.info(f"Renamed crop {crop_id} to '{new_name}': {updated_count} tasks updated")

        return {
            'message': f'Successfully renamed crop to {new_name}',
            'updated_tasks': updated_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rename Crop Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(data: ChatInput):
    """Chat endpoint for the Calendar AI Agent."""
    if not data.message or not data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply = agent.generate_response(data.message, data.context, data.history)
        return {'reply': reply}
    except Exception as e:
        logger.error(f"Chat Endpoint Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == '__main__':
    logger.info("Starting Smart Farming Calendar Service on Port 5004")
    uvicorn.run(app, host="0.0.0.0", port=5004)
