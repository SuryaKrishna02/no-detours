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
    
    def collect_context(self, queries: List[Dict[str, str]], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect context information based on search queries and features.
        
        Args:
            queries: List of dictionaries containing feature type, value, and search query
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
        for query_obj in queries:
            search_query = query_obj.get("search_query", "")
            if not search_query:
                continue
                
            results = self.search_api.search(search_query, num_results=3)
            context["search_results"].append({
                "feature_type": query_obj.get("feature_type", ""),
                "feature_value": query_obj.get("feature_value", ""),
                "query": search_query,
                "results": results
            })
        
        # Collect weather information if available
        if self.weather_api and features.get("place_to_visit"):
            try:
                weather_info = self.weather_api.get_forecast(
                    location=features["place_to_visit"]
                )
                context["weather_info"] = weather_info
            except Exception as e:
                print(f"Error fetching weather information: {e}")
        
        # Collect map information if available
        if self.maps_api and features.get("place_to_visit"):
            try:
                map_info = self.maps_api.get_location_info(features["place_to_visit"])
                context["map_info"] = map_info
            except Exception as e:
                print(f"Error fetching map information: {e}")
        
        return context