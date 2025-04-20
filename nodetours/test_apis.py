# test_nodetours_apis.py
import os
import json
import logging
from dotenv import load_dotenv
from api.nodetours_weather import WeatherAPI
from api.nodetours_maps import MapsAPI
from api.nodetours_search import SearchAPI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_weather_api():
    """Test the weather API."""
    print("\n=== Testing Weather API ===")
    
    weather_api = WeatherAPI()
    
    test_locations = ["New York", "London"]
    
    for location in test_locations:
        print(f"\nTesting weather for: {location}")
        forecast = weather_api.get_forecast(location, "next week")
        
        # Pretty print the result
        print(json.dumps(forecast, indent=2))

def test_maps_api():
    """Test the maps API."""
    print("\n=== Testing Maps API ===")
    
    maps_api = MapsAPI()
    
    test_locations = ["Chicago", "Paris"]
    
    for location in test_locations:
        print(f"\nTesting location info for: {location}")
        location_info = maps_api.get_location_info(location)
        
        # Pretty print the result
        print(json.dumps(location_info, indent=2))

def test_search_api():
    """Test the search API."""
    print("\n=== Testing Search API ===")
    
    search_api = SearchAPI()
    
    # test_queries = [
    #     "top attractions in Rome",
    #     "best restaurants in Tokyo"
    # ]
    test_queries1 =['Chicago top attractions and must-see places', 'Chicago weather in June', 'Family-friendly activities in Chicago']
    # test_queries =[ 'Best museums to visit in Chicago', 'Top parks in Chicago for families', 'Local food options for families in Chicago', 'Transportation options in Chicago for families']
    test_queries = [str(x) for x in test_queries1]
    # print(test_queries)
    
    for query in test_queries:
        print(f"\nTesting search for: {query}")
        results = search_api.search(query, num_results=2)
        
        # Pretty print the results
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    print("Testing API integrations...")
    print("Note: This will use your API keys if available, or fall back to mock data.")
    
    try:
        test_weather_api()
    except Exception as e:
        logger.error(f"Weather API test failed: {e}", exc_info=True)
    
    try:
        test_maps_api()
    except Exception as e:
        logger.error(f"Maps API test failed: {e}", exc_info=True)
    
    try:
        test_search_api()
    except Exception as e:
        logger.error(f"Search API test failed: {e}", exc_info=True)
    
    print("\nAPI testing complete!")