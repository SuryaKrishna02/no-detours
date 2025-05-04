"""
api/maps.py

Maps API wrapper for travel planning applications. Supports Google Maps geocoding 
with fallback to mock data when API keys are unavailable or requests fail.
"""
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
    """
    Wrapper for maps API providers that abstracts geocoding functionality.
    
    Supports Google Maps API with fallback to mock data when API keys are
    unavailable or requests fail. Designed to provide location information
    for travel planning applications.
    
    Attributes:
        provider (str): The maps API provider name ('googlemaps' or 'mock')
        api_key (str): API key for the selected provider
    """
    
    def __init__(self, provider: str = "googlemaps"):
        """
        Initialize the Maps API wrapper.
        
        Args:
            provider (str, optional): The maps API provider to use.
                                     Defaults to "googlemaps".
        
        Note:
            If Google Maps is selected but no API key is found in environment
            variables, automatically falls back to mock mode.
        """
        self.provider = provider.lower()
        
        if self.provider == "googlemaps":
            self.api_key = os.environ.get("MAPS_API_KEY")
            if not self.api_key:
                logger.warning("MAPS_API_KEY not found, falling back to mock mode")
                self.provider = "mock"
        
        logger.info(f"Initialized MapsAPI with provider: {self.provider}")
    
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """
        Get geocoding information about a specified location.
        
        Retrieves formatted address, latitude/longitude coordinates, and
        place ID for the specified location. Falls back to mock data if
        the API request fails.
        
        Args:
            location (str): The location name (city, country, etc.)
            
        Returns:
            Dict[str, Any]: Dictionary containing location information with keys:
                - formatted_address: Full formatted address string
                - location: Dict with 'lat' and 'lng' coordinates
                - place_id: Unique identifier for the location
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
        """
        Generate mock location information when real data is unavailable.
        
        Creates a consistent mock response format that matches the structure
        of real API responses for seamless fallback.
        
        Args:
            location (str): The location name to generate mock data for
            
        Returns:
            Dict[str, Any]: Dictionary with mock location data using the same
                           structure as real API responses
        """
        logger.info(f"Generating mock location information for {location}")
        
        return {
            "formatted_address": f"{location}, Country",
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            },
            "place_id": "mock-place-id"
        }