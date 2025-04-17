# app/modules/context_collector.py
from typing import Dict, List, Any
from api.nodetours_search import SearchAPI
from api.nodetours_maps import MapsAPI
from api.nodetours_weather import WeatherAPI

class ContextCollector:
    """Collects context information from various sources."""
    
    def __init__(self, search_api: SearchAPI, weather_api=None, maps_api=None):
        self.search_api = search_api
        self.weather_api = weather_api
        self.maps_api = maps_api
    
    def collect_context(self, queries: List[str], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect context information based on search queries and features.
        
        Args:
            queries: List of search queries
            features: Extracted travel features
            
        Returns:
            Dict with collected context information
        """
        context = {
            "search_results": [],
            "weather_info": {},
            "map_info": {}
        }
        
        # Collect search results
        for query in queries:
            results = self.search_api.search(query, num_results=3)
            context["search_results"].append({
                "query": query,
                "results": results
            })
        
        # Collect weather information if available
        if self.weather_api and features.get("destination") and features.get("dates"):
            try:
                weather_info = self.weather_api.get_forecast(
                    location=features["destination"],
                    dates=features["dates"]
                )
                context["weather_info"] = weather_info
            except Exception as e:
                print(f"Error fetching weather information: {e}")
        
        # Collect map information if available
        if self.maps_api and features.get("destination"):
            try:
                map_info = self.maps_api.get_location_info(features["destination"])
                context["map_info"] = map_info
            except Exception as e:
                print(f"Error fetching map information: {e}")
        
        return context