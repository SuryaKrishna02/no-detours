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
    
    def get_forecast(self, location: str) -> Dict[str, Any]:
        """
        Get weather forecast for a location and date range.
        
        Args:
            location: The location (city, country)
            
        Returns:
            Dict with weather forecast information
        """
        if self.provider == "openweathermap":
            try:
                # Simple implementation to get current weather
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "imperial"
                }
                
                response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=params)
                
                if response.status_code == 200:
                    logger.info("Successfully Fetched the 5-Day Weather Forecast")
                    data = response.json()
                    # Extract daily forecasts (every 8th entry since the API provides data in 3-hour intervals)
                    daily_forecasts = data["list"][::8]
                    weather_forecast = []
                    for day_num, forecast in enumerate(daily_forecasts):
                        weather_forecast.append(
                            {
                                "day": {day_num},
                                "min_temp": f"{forecast["main"]["temp_min"]}°F",
                                "max_temp": f"{forecast["main"]["temp_max"]}°F",
                                "feels_like": f"{forecast["main"]["feels_like"]}°F",
                                "description": forecast["weather"][0]["description"],
                                "wind_speed": f"{forecast['wind']["speed"]} mph"
                            }
                        )
                    
                    forecast = {
                        "location": location,
                        "five_day_forecast": weather_forecast
                    }
                    
                    return forecast
                else:
                    logger.warning(f"Failed to get weather data: {response.status_code}")
                    return self._get_mock_forecast(location)
            except Exception as e:
                logger.error(f"Error fetching weather data: {e}")
                return self._get_mock_forecast(location)
        
        return self._get_mock_forecast(location)
    
    def _get_mock_forecast(self, location: str) -> Dict[str, Any]:
        """Generate mock weather forecast."""
        logger.info(f"Generating mock weather forecast for {location}")
        
        return {
	    "location": "Bloomington",
        "five_day_forecast": [
            {
                "day": 1,
                "min_temp": "59.04°F",
                "max_temp": "61.83°F",
                "feels_like": "59.83°F",
                "description": "few clouds",
                "wind_speed": "3.11 mph"
            },
            {
                "day": 2,
                "min_temp": "62.56°F",
                "max_temp": "62.56°F",
                "feels_like": "61.34°F",
                "description": "clear sky",
                "wind_speed": "4.03 mph"
            },
            {
                "day": 3,
                "min_temp": "60.73°F",
                "max_temp": "60.73°F",
                "feels_like": "59.32°F",
                "description": "few clouds",
                "wind_speed": "3.6 mph"
            },
            {
                "day": 4,
                "min_temp": "66°F",
                "max_temp": "66°F",
                "feels_like": "65.08°F",
                "description": "scattered clouds",
                "wind_speed": "4.79 mph"
            },
            {
                "day": 5,
                "min_temp": "58.48°F",
                "max_temp": "58.48°F",
                "feels_like": "57.31°F",
                "description": "overcast clouds",
                "wind_speed": "6.78 mph"
            }
	]
}