# api/app.py
import os
import yaml
import logging
from typing import Dict, Any, List
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

from app.agent import TravelPlannerAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define request models
class UserInput(BaseModel):
    text: str

# Load configuration
def load_config(config_path: str):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
config_path = os.path.join(BASE_DIR, 'config', 'config.yaml')
config = load_config(config_path)

# Initialize agent
agent = TravelPlannerAgent(config)

# Initialize FastAPI app
app = FastAPI(
    title="NoDetours Travel Planner",
    description="AI-powered personalized travel planning assistant",
    version=config.get("app", {}).get("version", "0.1.0")
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Define routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/plan")
async def create_plan(user_input: UserInput):
    """Generate a travel plan based on user input."""
    try:
        logger.info(f"Received request to create plan with input: {user_input.text[:50]}...")
        
        if not user_input.text:
            return JSONResponse(content={"error": "Input text cannot be empty"}, status_code=400)
        
        result = agent.process_input(user_input.text)
        
        # Verify the result contains the necessary fields
        if not result.get("itinerary"):
            logger.warning("No itinerary was generated in the result")
            result["itinerary"] = "I couldn't generate a detailed itinerary based on your input. Please provide more specific travel details like destination, dates, and preferences."
        
        logger.info("Successfully generated travel plan")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error generating travel plan: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": f"Failed to generate travel plan: {str(e)}"}, 
            status_code=500
        )

@app.get("/api/history")
async def get_history():
    """Get conversation history."""
    try:
        return {"history": agent.get_conversation_history()}
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": f"Failed to get history: {str(e)}"}, 
            status_code=500
        )