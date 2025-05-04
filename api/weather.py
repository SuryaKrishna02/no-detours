"""
api/weather.py

Wrapper for weather API services that provides weather forecast data for travel planning.
Supports OpenWeatherMap API with mock data fallback when API keys are unavailable.
"""

import os
import logging
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class WeatherAPI:
    """
    Wrapper for weather API providers that retrieves forecast data.
    
    This class provides an interface to weather APIs, primarily OpenWeatherMap,
    with a fallback to mock data when API credentials are unavailable.
    
    Attributes:
        provider (str): The weather API provider name (e.g., "openweathermap")
        api_key (str): The API key for authentication with the provider
    """
    
    def __init__(self, provider: str = "openweathermap"):
        """
        Initialize the WeatherAPI with a specific provider.
        
        Args:
            provider (str, optional): The weather API provider to use. 
                                     Defaults to "openweathermap".
        
        Note:
            Falls back to "mock" mode if the required API key is not found
            in environment variables.
        """
        self.provider = provider.lower()
        
        if self.provider == "openweathermap":
            self.api_key = os.environ.get("WEATHER_API_KEY")
            if not self.api_key:
                logger.warning("WEATHER_API_KEY not found, falling back to mock mode")
                self.provider = "mock"
        
        logger.info(f"Initialized WeatherAPI with provider: {self.provider}")
    
    def get_forecast(self, location: str) -> Dict[str, Any]:
        """
        Get a 5-day weather forecast for the specified location.
        
        Retrieves weather data from the configured provider, extracting daily
        forecast data and formatting it consistently. Falls back to mock data
        when the API call fails or when in mock mode.
        
        Args:
            location (str): The location name (e.g., "Paris, France")
            
        Returns:
            Dict[str, Any]: A dictionary containing forecast information, with
                           'location' and 'five_day_forecast' keys. The forecast
                           includes daily min/max temperatures, feels-like temperature,
                           weather description, and wind speed.
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
        """
        Generate a mock weather forecast when actual API data is unavailable.
        
        This method provides consistent mock data for testing or when API
        access is unavailable.
        
        Args:
            location (str): The location for which to generate mock data
            
        Returns:
            Dict[str, Any]: A dictionary with mock forecast data, using the
                          same structure as the actual API response
        """
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