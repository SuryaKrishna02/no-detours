# nodetours_weather.py
import os
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class WeatherAPI:
    """Wrapper for weather API providers."""
    
    def __init__(self, provider: str = "openweathermap"):
        self.provider = provider.lower()
        
        if self.provider == "openweathermap":
            self.api_key = os.environ.get("WEATHER_API_KEY")
            if not self.api_key:
                logger.warning("WEATHER_API_KEY not found, falling back to mock mode")
                self.provider = "mock"
        
        logger.info(f"Initialized WeatherAPI with provider: {self.provider}")
    
    def get_forecast(self, location: str, dates: str) -> Dict[str, Any]:
        """
        Get weather forecast for a location and date range.
        
        Args:
            location: The location (city, country)
            dates: Date range string
            
        Returns:
            Dict with weather forecast information
        """
        if self.provider == "openweathermap":
            try:
                # Simple implementation to get current weather
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    weather = {
                        "location": location,
                        "current": {
                            "temp": data.get("main", {}).get("temp"),
                            "feels_like": data.get("main", {}).get("feels_like"),
                            "humidity": data.get("main", {}).get("humidity"),
                            "description": data.get("weather", [{}])[0].get("description") if data.get("weather") else "",
                            "wind_speed": data.get("wind", {}).get("speed")
                        }
                    }
                    
                    return weather
                else:
                    logger.warning(f"Failed to get weather data: {response.status_code}")
                    return self._get_mock_forecast(location, dates)
            except Exception as e:
                logger.error(f"Error fetching weather data: {e}")
                return self._get_mock_forecast(location, dates)
        
        return self._get_mock_forecast(location, dates)
    
    def _get_mock_forecast(self, location: str, dates: str) -> Dict[str, Any]:
        """Generate mock weather forecast."""
        logger.info(f"Generating mock weather forecast for {location}")
        
        return {
            "location": location,
            "current": {
                "temp": 22,
                "feels_like": 23,
                "humidity": 65,
                "description": "Partly cloudy with occasional showers",
                "wind_speed": 10
            }
        }