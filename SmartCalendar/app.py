
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import logging
import uvicorn
from calendar_agent import CalendarAgent
import uuid

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

# In-memory task storage (can be upgraded to database later)
tasks_db = []

# Pydantic Models for Input Validation
class ScheduleInput(BaseModel):
    crop: str
    location: str
    planting_date: str  # Format: YYYY-MM-DD

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
    status: Optional[str] = None # pending | completed | updated | deleted
    phase: Optional[str] = None

class ChatInput(BaseModel):
    message: str
    context: dict = {}
    history: list = []

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
            <p>AI-Powered Farming Schedule & Task Management (FastAPI).</p>
            <div class="status">Status: <strong>Active</strong></div>
            <div class="ai-status">AI Agent: {ai_status}</div>
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
    """
    if not agent.is_active:
        raise HTTPException(status_code=503, detail="AI service is currently unavailable. Please check server logs/keys.")

    try:
        logger.info(f"Generating schedule for {data.crop} in {data.location}, planting on {data.planting_date}")
        
        # Validate date format
        try:
            datetime.strptime(data.planting_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Create a unique crop_id for this session
        crop_id = f"crop_{uuid.uuid4().hex[:8]}"

        # Generate schedule using AI
        tasks = agent.generate_farming_schedule(data.crop, data.location, data.planting_date, crop_id=crop_id)
        
        if not tasks:
            raise HTTPException(status_code=500, detail="Failed to generate schedule.")
        
        # Add tasks to database
        new_tasks = []
        for task in tasks:
            task_entry = {
                'id': str(uuid.uuid4()),
                'task_id': task.get('task_id', str(uuid.uuid4())),
                'crop_id': crop_id,
                'crop_name': data.crop,
                'phase': task.get('phase', 'General'),
                'title': task.get('title', 'Untitled Task'),
                'date': task.get('date', data.planting_date),
                'category': task.get('category', 'general'),
                'description': task.get('description', ''),
                'priority': task.get('priority', 'medium'),
                'status': task.get('status', 'pending'),
                'completed': False,
                'location': data.location
            }
            tasks_db.append(task_entry)
            new_tasks.append(task_entry)
        
        return {
            'message': f'Successfully generated {len(tasks)} tasks for {data.crop}',
            'crop_id': crop_id,
            'tasks': new_tasks,
            'crop': data.crop,
            'location': data.location
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schedule Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_task")
async def add_task(data: TaskInput):
    """
    Add a custom farming task to the calendar.
    """
    try:
        # Validate date format
        try:
            datetime.strptime(data.date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
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
            'completed': False
        }
        
        tasks_db.append(task_entry)
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
        
        # Sort by date
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
    """
    Update a task's details with strict consistency rules.
    """
    try:
        # Find task
        task = next((t for t in tasks_db if t['id'] == task_id), None)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        today = date.today().strftime('%Y-%m-%d')
        
        # Update fields
        if data.title is not None:
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
            task['priority'] = data.priority
        if data.completed is not None:
            task['completed'] = data.completed
            task['status'] = 'completed' if data.completed else 'pending'
        if data.phase is not None:
            task['phase'] = data.phase
        if data.status is not None:
             task['status'] = data.status
        elif not data.completed:
             task['status'] = 'updated'

        logger.info(f"Updated task {task_id} for crop {task.get('crop_name')}")
        
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
    """
    Delete a task with lifecycle awareness.
    """
    try:
        task = next((t for t in tasks_db if t['id'] == task_id), None)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        critical_tasks = ['sowing', 'planting', 'transplanting']
        is_critical = task.get('category', '').lower() in critical_tasks or 'sow' in task.get('title', '').lower()
        
        tasks_db.remove(task)
        logger.info(f"Deleted task {task_id} ({task.get('title')})")
        
        return {
            'message': 'Task deleted successfully',
            'task_id': task_id,
            'is_critical': is_critical,
            'crop_id': task.get('crop_id'),
            'warning': "Critical task deleted. Crop lifecycle may be inconsistent." if is_critical else None
        }
        
    except HTTPException:
        raise
@app.delete("/delete_crop/{crop_id}")
async def delete_crop(crop_id: str):
    """
    Delete all tasks associated with a specific crop ID.
    """
    try:
        global tasks_db
        initial_count = len(tasks_db)
        tasks_db = [t for t in tasks_db if t.get('crop_id') != crop_id]
        deleted_count = initial_count - len(tasks_db)
        
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
    """
    Rename all occurrences of a crop name for a specific crop ID.
    """
    try:
        updated_count = 0
        for task in tasks_db:
            if task.get('crop_id') == crop_id:
                task['crop_name'] = new_name
                updated_count += 1
        
        logger.info(f"Renamed crop {crop_id} to {new_name}: {updated_count} tasks updated")
        
        return {
            'message': f'Successfully renamed crop to {new_name}',
            'updated_tasks': updated_count
        }
    except Exception as e:
        logger.error(f"Rename Crop Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(data: ChatInput):
    """
    Chat endpoint for the Calendar AI Agent.
    """
    if not data.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        reply = agent.generate_response(data.message, data.context, data.history)
        return {'reply': reply}
    except Exception as e:
        logger.error(f"Chat Endpoint Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == '__main__':
    logger.info("Starting Service on Port 5004")
    uvicorn.run(app, host="0.0.0.0", port=5004)
