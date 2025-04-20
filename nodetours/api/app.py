# api/app.py
import os
import yaml
import logging
import re
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
        
        # Process the input with our agent - no validation requirements
        result = agent.process_input(user_input.text)
        
        # Check for trip_details
        trip_details = result.get("trip_details", {})
        if trip_details:
            logger.info(f"Trip details: {trip_details}")
        
        # Verify the result contains the necessary fields
        if not result.get("itinerary"):
            logger.warning("No itinerary was generated in the result")
            result["itinerary"] = "I couldn't generate a detailed itinerary based on your input. Please provide more specific travel details like destination, dates, and preferences."
            
        # Verify the itinerary has the correct number of days
        itinerary = result.get("itinerary", "")
        trip_details = result.get("trip_details", {})
        expected_days = trip_details.get("duration_days", 0)
        
        if expected_days > 0 and itinerary:
            # Count day headers in the itinerary
            import re
            day_headers = re.findall(r'## Day \d+', itinerary)
            day_count = len(day_headers)
            
            logger.info(f"Expected {expected_days} days, found {day_count} day headers")
            
            # If we have a significant mismatch, log a warning
            if day_count < expected_days:
                logger.warning(f"Itinerary has fewer days than requested. Expected: {expected_days}, Found: {day_count}")
                # We'll still return what we have, as the frontend will handle the display
            
        # Log each component for debugging purposes
        logger.info(f"Generated itinerary length: {len(result.get('itinerary', ''))}")
        logger.info(f"Generated packing list length: {len(result.get('packing_list', ''))}")
        
        # Specifically check the budget content
        budget = result.get("estimated_budget", "")
        logger.info(f"Generated budget length: {len(budget)}")
        logger.info(f"Budget excerpt: {budget[:100]}...")
        
        # Make sure budget is properly formatted for the frontend
        if budget and "Budget Estimate" not in budget:
            # Try to add a title if it's missing
            logger.warning("Budget estimate is missing a title, adding one")
            destination = trip_details.get("destination", "Your Trip")
            result["estimated_budget"] = f"### Budget Estimate for {destination}\n\n{budget}"
        
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