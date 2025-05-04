"""
app/modules/context_collector.py

Context collection module that gathers information from various sources using search, scraping, weather and maps APIs.
Serves as an information aggregator for the travel planning system, fetching relevant data based on search queries and features.
"""

import logging
from api.maps import MapsAPI
from api.search import SearchAPI
from api.weather import WeatherAPI
from typing import Dict, List, Any
from api.scrape import WebScrapperAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextCollector:
    """
    Collects context information from various external sources.
    
    This class coordinates data gathering from search, scraping, weather, and maps APIs
    to compile comprehensive context information for travel planning purposes.
    """
    
    def __init__(self, search_api: SearchAPI, scrape_api: WebScrapperAPI, weather_api: WeatherAPI = None, maps_api: MapsAPI = None):
        """
        Initialize the ContextCollector with required API interfaces.
        
        Args:
            search_api: API interface for performing web searches
            scrape_api: API interface for web scraping
            weather_api: Optional API interface for weather forecasts
            maps_api: Optional API interface for geographical data
        """
        self.search_api = search_api
        self.weather_api = weather_api
        self.maps_api = maps_api
        self.scrape_api = scrape_api
        logger.info("Initialized Search Query Feature Extractor with provider")
    
    def collect_context(self, queries: List[Dict[str, str]], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect context information based on search queries and extracted features.
        
        This method orchestrates data collection by:
        1. Executing web searches and scraping information
        2. Fetching weather forecasts if available
        3. Retrieving geographical information if available
        
        Args:
            queries: List of dictionaries containing feature type, value, and search query
            features: Extracted travel features including destination, preferences, etc.
            
        Returns:
            Dictionary with collected context information organized by source:
            - search_results: Information from web searches
            - weather_info: Weather forecast data (if available)
            - map_info: Geographical information (if available)
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
                
            search_links = self.search_api.search(search_query, num_results=1)
            results = []
            for link in search_links:
                places_info = self.scrape_api.scrape(
                    url=link
                )
                results.extend(places_info)

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