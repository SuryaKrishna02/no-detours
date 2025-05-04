# nodetours_maps.py
import os
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class MapsAPI:
    """Wrapper for maps API providers."""
    
    def __init__(self, provider: str = "googlemaps"):
        self.provider = provider.lower()
        
        if self.provider == "googlemaps":
            self.api_key = os.environ.get("MAPS_API_KEY")
            if not self.api_key:
                logger.warning("MAPS_API_KEY not found, falling back to mock mode")
                self.provider = "mock"
        
        logger.info(f"Initialized MapsAPI with provider: {self.provider}")
    
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """
        Get information about a location.
        
        Args:
            location: The location (city, country)
            
        Returns:
            Dict with location information
        """
        if self.provider == "googlemaps":
            try:
                params = {
                    "address": location,
                    "key": self.api_key
                }
                
                response = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "OK" and data.get("results"):
                        result = data["results"][0]
                        
                        location_info = {
                            "formatted_address": result.get("formatted_address", ""),
                            "location": result.get("geometry", {}).get("location", {}),
                            "place_id": result.get("place_id", "")
                        }
                        
                        return location_info
                    else:
                        logger.warning(f"Failed to get location data: {data.get('status')}")
                        return self._get_mock_location_info(location)
                else:
                    logger.warning(f"Failed to get location data: {response.status_code}")
                    return self._get_mock_location_info(location)
            except Exception as e:
                logger.error(f"Error getting location info: {e}")
                return self._get_mock_location_info(location)
        
        return self._get_mock_location_info(location)
    
    def _get_mock_location_info(self, location: str) -> Dict[str, Any]:
        """Generate mock location information."""
        logger.info(f"Generating mock location information for {location}")
        
        return {
            "formatted_address": f"{location}, Country",
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            },
            "place_id": "mock-place-id"
        }