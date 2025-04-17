# app/agent.py
from typing import Dict, List, Any
import logging

from api.llm_provider import LLMProvider
from api.nodetours_search import SearchAPI
from api.nodetours_maps import MapsAPI 
from api.nodetours_weather import WeatherAPI
from app.modules.search_query_extractor import SearchQueryExtractor
from app.modules.search_query_generator import SearchQueryGenerator
from app.modules.context_collector import ContextCollector
from app.modules.output_generator import OutputGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelPlannerAgent:
    """Main Travel Planner Agent class that orchestrates the planning process."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Travel Planner Agent with configuration.
        
        Args:
            config: Configuration dictionary
        """
        logger.info("Initializing TravelPlannerAgent")
        
        # Initialize LLM provider
        llm_config = config.get("llm", {})
        self.llm_provider = LLMProvider(
            provider=llm_config.get("provider", "anthropic"),
            model=llm_config.get("model", "claude-3-5-sonnet"),
            temperature=llm_config.get("temperature", 0.7),
            max_tokens=llm_config.get("max_tokens", 4000)
        )
        
        # # Initialize APIs with mock implementations for the MVP
        # self.search_api = SearchAPI()
        # self.weather_api = WeatherAPI()
        # self.maps_api = MapsAPI()

        logger.info("Initializing TravelPlannerAgent")
        
        # Initialize APIs with real implementations
        api_config = config.get("apis", {})
        
        self.weather_api = WeatherAPI(
            provider=api_config.get("weather", {}).get("provider", "openweathermap")
        )
        
        self.maps_api = MapsAPI(
            provider=api_config.get("maps", {}).get("provider", "googlemaps")
        )
        
        self.search_api = SearchAPI(
            provider=api_config.get("search", {}).get("provider", "serpapi")
        )
        
        # Initialize modules
        self.query_extractor = SearchQueryExtractor(self.llm_provider)
        self.query_generator = SearchQueryGenerator(self.llm_provider)
        self.context_collector = ContextCollector(
            search_api=self.search_api,
            weather_api=self.weather_api,
            maps_api=self.maps_api
        )
        self.output_generator = OutputGenerator(self.llm_provider)
        
        # Store conversation history
        self.conversation_history = []
        
        # Store the last generated itinerary and features
        self.last_itinerary = ""
        self.last_features = {}
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and generate travel plans.
        
        Args:
            user_input: The user's text input
            
        Returns:
            Dict with generated travel plans and recommendations
        """
        logger.info("Processing user input")
        
        try:
            # 1. Extract features from user input
            features = self.query_extractor.extract_features(user_input)
            logger.info(f"Extracted features: {features}")
            
            # 2. Generate search queries
            queries = self.query_generator.generate_queries(features)
            logger.info(f"Generated queries: {queries}")
            
            # 3. Collect context information
            context = self.context_collector.collect_context(queries, features)
            logger.info("Collected context information")
            
            # 4. Generate travel plans
            output = self.output_generator.generate_itinerary(features, context)
            logger.info("Generated travel plan output")
            
            # 5. Add fallback responses if any component failed
            if not output.get("itinerary"):
                logger.warning("No itinerary was generated, providing fallback")
                output["itinerary"] = self._generate_fallback_itinerary(features)
            
            if not output.get("packing_list"):
                logger.warning("No packing list was generated, providing fallback")
                output["packing_list"] = self._generate_fallback_packing_list(features)
            
            if not output.get("estimated_budget"):
                logger.warning("No budget estimate was generated, providing fallback")
                output["estimated_budget"] = self._generate_fallback_budget(features)
            
            # Store for later use
            self.last_itinerary = output.get("itinerary", "")
            self.last_features = features
            
            # 6. Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": output.get("itinerary", "")
            })
            
            return output
        
        except Exception as e:
            logger.error(f"Error in process_input: {str(e)}", exc_info=True)
            # Return a basic response in case of error
            return {
                "itinerary": "I apologize, but I couldn't generate a travel plan due to an error. Please try again with more specific details about your destination, dates, and preferences.",
                "packing_list": "Unable to generate packing list due to an error.",
                "estimated_budget": "Unable to generate budget estimate due to an error."
            }
    
    def _generate_fallback_itinerary(self, features: Dict[str, Any]) -> str:
        """Generate a fallback itinerary if the main generation fails."""
        destination = features.get("destination", "your destination")
        
        fallback = f"""
# Travel Itinerary for {destination}

I've prepared a basic itinerary outline for your trip to {destination}. To create a more detailed plan, I'd need more specific information about your travel dates, preferences, and constraints.

## General Recommendations

- Research the top attractions in {destination}
- Look for accommodation in central areas for easy access to attractions
- Check the local weather forecast before your trip
- Consider local transportation options
- Research local cuisine and popular restaurants

Please provide more details about your trip for a customized itinerary including day-by-day activities, accommodation recommendations, and local tips.
        """
        
        return fallback.strip()
    
    def _generate_fallback_packing_list(self, features: Dict[str, Any]) -> str:
        """Generate a fallback packing list if the main generation fails."""
        destination = features.get("destination", "your destination")
        
        fallback = f"""
# Packing Essentials for {destination}

Here's a general packing list to help you prepare:

## Documents
- Passport/ID
- Travel insurance information
- Hotel/accommodation confirmations
- Flight/transportation tickets

## Clothing
- Weather-appropriate clothing
- Comfortable walking shoes
- Light jacket or sweater
- Sleepwear

## Toiletries
- Toothbrush and toothpaste
- Shampoo and soap
- Sunscreen
- Personal medications

## Electronics
- Phone and charger
- Camera
- Power adapter if traveling internationally

For a more specific packing list, please provide details about your travel season, planned activities, and any special requirements.
        """
        
        return fallback.strip()
    
    def _generate_fallback_budget(self, features: Dict[str, Any]) -> str:
        """Generate a fallback budget if the main generation fails."""
        destination = features.get("destination", "your destination")
        
        fallback = f"""
# Budget Estimate for {destination}

Without specific details about your travel style and preferences, I can only provide a general budget framework:

## Approximate Costs

- **Accommodation**: Varies widely from budget hostels to luxury hotels
- **Transportation**: Consider local public transit, taxis, or rental cars
- **Food**: Budget for meals according to your dining preferences
- **Activities**: Research ticket prices for attractions you wish to visit
- **Miscellaneous**: Include a buffer for souvenirs and unexpected expenses

For a detailed budget estimate, please provide information about your accommodation preferences, dining habits, planned activities, and travel style.
        """
        
        return fallback.strip()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history