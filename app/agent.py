"""
app/agent.py

Travel Planner Agent orchestrator module that coordinates the end-to-end travel planning process.
This module integrates various components to generate personalized travel plans from user queries.
"""

import logging
from api.maps import MapsAPI 
from api.search import SearchAPI
from typing import Dict, List, Any
from api.weather import WeatherAPI
from api.scrape import WebScrapperAPI
from api.llm_provider import LLMProvider
from app.modules.guardrail import Guardrail
from app.modules.output_generator import OutputGenerator
from app.modules.context_collector import ContextCollector
from app.modules.search_query_extractor import SearchQueryExtractor
from app.modules.search_query_generator import SearchQueryGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelPlannerAgent:
    """
    Main Travel Planner Agent class that orchestrates the end-to-end planning process.
    
    This class integrates multiple components to extract features from user queries,
    generate relevant search queries, collect contextual information, and produce
    comprehensive travel plans with itineraries, packing lists, and budget estimates.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Travel Planner Agent with configuration.
        
        Args:
            config: Configuration dictionary containing LLM and API settings
                   with provider details, model names, and parameters
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
        
        # Initialize APIs with real implementations
        api_config = config.get("apis", {})
        
        self.weather_api = WeatherAPI(
            provider=api_config.get("weather", {}).get("provider", "openweathermap")
        )
        
        self.maps_api = MapsAPI(
            provider=api_config.get("maps", {}).get("provider", "googlemaps")
        )
        
        self.search_api = SearchAPI()
        self.scrape_api = WebScrapperAPI()
        
        # Initialize modules
        self.guardrail = Guardrail(self.llm_provider)
        self.query_extractor = SearchQueryExtractor(self.llm_provider)
        self.query_generator = SearchQueryGenerator(self.llm_provider)
        self.context_collector = ContextCollector(
            search_api=self.search_api,
            weather_api=self.weather_api,
            maps_api=self.maps_api,
            scrape_api=self.scrape_api
        )
        self.output_generator = OutputGenerator(self.llm_provider)
        
        # Store conversation history
        self.conversation_history = []
        
        # Store the last generated itinerary and features
        self.last_itinerary = ""
        self.last_features = {}
    
    def process_input(self, user_input: str, eval: bool = False) -> Dict[str, Any]:
        """
        Process user input and generate comprehensive travel plans.
        
        This method implements the full pipeline: validating input, extracting features,
        generating search queries, collecting context, and creating travel plans with
        fallback mechanisms if any component fails.
        
        Args:
            user_input: The user's text input containing travel preferences
            eval: Flag indicating whether to return evaluation data structure
                  instead of just the travel plan output
            
        Returns:
            If eval=False: Dictionary with generated travel plans including itinerary,
                          packing list, and budget estimation
            If eval=True: Dictionary with features, queries, context, and output for
                         evaluation purposes
        """
        logger.info("Processing user input")
        
        try:
            # Input Validation
            is_valid = self.guardrail.validate_input(user_input)
            if not is_valid:
                raise ValueError("Invalid User Input.")
            logger.info("Validated the User Input")

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

            if eval:
                eval_output = {
                    "features": features,
                    "queries": queries,
                    "context": context,
                    "output": output
                }
                return eval_output
            
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
        """
        Generate a fallback itinerary if the main generation fails.
        
        Creates a basic template itinerary based on the destination
        when the primary itinerary generation process encounters an error.
        
        Args:
            features: Dictionary of extracted features from the user query
            
        Returns:
            Formatted string containing a basic itinerary template
        """
        destination = features.get("place_to_visit", "your destination")
        
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
        """
        Generate a fallback packing list if the main generation fails.
        
        Creates a generic packing list based on the destination
        when the primary packing list generation encounters an error.
        
        Args:
            features: Dictionary of extracted features from the user query
            
        Returns:
            Formatted string containing a basic packing list
        """
        destination = features.get("place_to_visit", "your destination")
        
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
        """
        Generate a fallback budget if the main generation fails.
        
        Creates a generic budget estimate framework based on the destination
        when the primary budget generation process encounters an error.
        
        Args:
            features: Dictionary of extracted features from the user query
            
        Returns:
            Formatted string containing a basic budget estimate template
        """
        destination = features.get("place_to_visit", "your destination")
        
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
        Get the conversation history between user and assistant.
        
        Retrieves the stored conversation messages for context-aware
        responses in follow-up interactions.
        
        Returns:
            List of conversation message dictionaries with role and content
        """
        return self.conversation_history