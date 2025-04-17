# app/modules/output_generator.py
import logging
from typing import Dict, List, Any
from api.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutputGenerator:
    """Generates travel itineraries and recommendations."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def generate_itinerary(self, 
                          features: Dict[str, Any], 
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a travel itinerary based on features and context.
        
        Args:
            features: Extracted travel features
            context: Collected context information
            
        Returns:
            Dict with generated itinerary
        """
        logger.info("Generating travel itinerary")
        
        # Prepare context for the prompt
        search_context = self._format_search_context(context.get("search_results", []))
        weather_context = self._format_weather_context(context.get("weather_info", {}))
        location_context = self._format_location_context(context.get("map_info", {}))
        
        system_prompt = """
        You are a personalized travel planning assistant called NoDetours.
        Your goal is to create detailed, personalized travel itineraries based on user preferences,
        external data about destinations, and current context (like weather conditions).
        
        Create a comprehensive travel itinerary that includes:
        1. A day-by-day schedule with activities and attractions
        2. Recommended accommodations
        3. Transportation options
        4. Weather-appropriate guidance
        5. Dining recommendations
        6. Estimated costs
        7. Tips specific to the destination
        
        Your itinerary should be personalized based on the user's preferences and constraints.
        Be specific, practical, and provide actionable recommendations.
        
        Format your response in Markdown with clear sections and bullet points.
        """
        
        user_prompt = f"""
        Please create a travel itinerary for me based on the following information:
        
        ## My Travel Details
        Destination: {features.get('destination', 'Not specified')}
        Dates: {features.get('dates', 'Not specified')}
        Duration: {features.get('duration', 'Not specified')}
        Preferences: {', '.join(features.get('preferences', [])) or 'Not specified'}
        Constraints: {', '.join(features.get('constraints', [])) or 'Not specified'}
        Transportation: {features.get('transportation', 'Not specified')}
        Accommodation: {features.get('accommodation', 'Not specified')}
        Travel group: {features.get('travel_group', 'Not specified')}
        
        ## Destination Information
        {search_context}
        
        ## Weather Information
        {weather_context}
        
        ## Location Information
        {location_context}
        """
        
        try:
            itinerary_text = self.llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            logger.info("Successfully generated itinerary")
            
            return {
                "itinerary": itinerary_text,
                "packing_list": self.generate_packing_list(features, context),
                "estimated_budget": self.estimate_budget(features, context)
            }
        except Exception as e:
            logger.error(f"Error generating itinerary: {e}", exc_info=True)
            return {
                "itinerary": "I apologize, but I couldn't generate a detailed itinerary. Please try again with more specific information about your trip.",
                "packing_list": "",
                "estimated_budget": ""
            }
    
    def generate_packing_list(self, 
                             features: Dict[str, Any], 
                             context: Dict[str, Any]) -> str:
        """Generate a packing list based on destination, weather, and activities."""
        logger.info("Generating packing list")
        
        system_prompt = """
        You are a travel planning assistant. Your task is to create a comprehensive 
        packing list based on the destination, weather conditions, and planned activities.
        Be specific and practical.
        
        Format your response in Markdown with clear sections and bullet points.
        """
        
        # Format weather information
        weather_info = context.get("weather_info", {})
        weather_summary = self._format_weather_context(weather_info)
        
        user_prompt = f"""
        Please create a packing list for a trip to {features.get('destination', '')}.
        
        Trip details:
        - Duration: {features.get('duration', 'Not specified')}
        - Weather: {weather_summary}
        - Activities: {', '.join(features.get('preferences', [])) or 'Not specified'}
        - Travel group: {features.get('travel_group', 'Not specified')}
        """
        
        try:
            return self.llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as e:
            logger.error(f"Error generating packing list: {e}", exc_info=True)
            return "I apologize, but I couldn't generate a packing list. Please try again with more specific information about your trip."
    
    def estimate_budget(self, 
                       features: Dict[str, Any], 
                       context: Dict[str, Any]) -> str:
        """Estimate a budget range based on destination and preferences."""
        logger.info("Generating budget estimate")
        
        system_prompt = """
        You are a travel budget estimator. Your task is to provide a reasonable 
        budget estimate based on the destination, accommodation preferences, 
        activities, and travel style. Provide a breakdown of costs for:
        
        1. Accommodation
        2. Transportation
        3. Food and dining
        4. Activities and attractions
        5. Miscellaneous expenses
        
        Give a range (min-max) for each category and a total estimated budget.
        Format your response in Markdown with clear sections and bullet points.
        """
        
        user_prompt = f"""
        Please estimate a budget for a trip to {features.get('destination', '')}.
        
        Trip details:
        - Duration: {features.get('duration', 'Not specified')}
        - Accommodation: {features.get('accommodation', 'Not specified')}
        - Transportation: {features.get('transportation', 'Not specified')}
        - Activities: {', '.join(features.get('preferences', [])) or 'Not specified'}
        - Travel group: {features.get('travel_group', 'Not specified')}
        - Constraints: {', '.join(features.get('constraints', [])) or 'Not specified'}
        """
        
        try:
            return self.llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as e:
            logger.error(f"Error generating budget estimate: {e}", exc_info=True)
            return "I apologize, but I couldn't generate a budget estimate. Please try again with more specific information about your trip."
    
    def _format_search_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results for the prompt."""
        if not search_results:
            return "No search results available."
        
        context = []
        
        for query_results in search_results:
            query = query_results.get("query", "")
            results = query_results.get("results", [])
            
            if results:
                context.append(f"Information about: {query}")
                for result in results:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    context.append(f"- {title}: {snippet}")
                context.append("")  # Add blank line between query groups
        
        return "\n".join(context)
    
    def _format_weather_context(self, weather_info: Dict[str, Any]) -> str:
        """Format weather information for the prompt."""
        if not weather_info:
            return "No weather information available."
        
        location = weather_info.get("location", "")
        current = weather_info.get("current", {})
        forecast = weather_info.get("forecast", [])
        
        context = []
        
        # Current weather
        if current:
            temp = current.get("temp")
            feels_like = current.get("feels_like")
            description = current.get("description", "")
            
            context.append(f"Current weather in {location}:")
            if temp is not None:
                context.append(f"- Temperature: {temp}°C")
            if feels_like is not None:
                context.append(f"- Feels like: {feels_like}°C")
            if description:
                context.append(f"- Conditions: {description}")
            context.append("")  # Add blank line
        
        # Forecast
        if forecast:
            context.append(f"Weather forecast for {location}:")
            for day in forecast:
                date = day.get("date", "")
                avg_temp = day.get("avg_temp")
                description = day.get("description", "")
                
                if date and avg_temp is not None:
                    context.append(f"- {date}: {avg_temp}°C, {description}")
            context.append("")  # Add blank line
        
        return "\n".join(context)
    
    def _format_location_context(self, location_info: Dict[str, Any]) -> str:
        """Format location information for the prompt."""
        if not location_info:
            return "No location information available."
        
        address = location_info.get("formatted_address", "")
        nearby_places = location_info.get("nearby_places", {})
        
        context = []
        
        if address:
            context.append(f"Location: {address}")
            context.append("")  # Add blank line
        
        # Nearby places
        if nearby_places:
            context.append("Nearby places of interest:")
            
            # Tourist attractions
            attractions = nearby_places.get("tourist_attraction", [])
            if attractions:
                context.append("Tourist Attractions:")
                for place in attractions:
                    name = place.get("name", "")
                    rating = place.get("rating", "")
                    vicinity = place.get("vicinity", "")
                    
                    if name:
                        context.append(f"- {name} ({rating}/5) - {vicinity}")
                context.append("")  # Add blank line
            
            # Restaurants
            restaurants = nearby_places.get("restaurant", [])
            if restaurants:
                context.append("Restaurants:")
                for place in restaurants:
                    name = place.get("name", "")
                    rating = place.get("rating", "")
                    vicinity = place.get("vicinity", "")
                    
                    if name:
                        context.append(f"- {name} ({rating}/5) - {vicinity}")
                context.append("")  # Add blank line
            
            # Hotels
            hotels = nearby_places.get("hotel", [])
            if hotels:
                context.append("Hotels:")
                for place in hotels:
                    name = place.get("name", "")
                    rating = place.get("rating", "")
                    vicinity = place.get("vicinity", "")
                    
                    if name:
                        context.append(f"- {name} ({rating}/5) - {vicinity}")
                context.append("")  # Add blank line
        
        return "\n".join(context)