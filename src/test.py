# Importing the requests module
import os
import requests
from dotenv import load_dotenv

load_dotenv()
city =  "Bloomington"

base_url = "https://api.openweathermap.org/data/2.5/forecast"
params = {
    "q": "Bloomington",
    "appid": os.getenv("WEATHER_API_KEY"),
    "units": "imperial"
}

response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=params)

if response.status_code == 200:
    data = response.json()
    # Extract daily forecasts (every 8th entry since the API provides data in 3-hour intervals)
    daily_forecasts = data["list"][::8]
    weather_forecast = []
    for day_num, forecast in enumerate(daily_forecasts):
        weather_forecast.append(
            {
                "day": day_num+1,
                "min_temp": f"{forecast["main"]["temp_min"]}°F",
                "max_temp": f"{forecast["main"]["temp_max"]}°F",
                "feels_like": f"{forecast["main"]["feels_like"]}°F",
                "description": forecast["weather"][0]["description"],
                "wind_speed": f"{forecast['wind']["speed"]} mph"
            }
        )
    
    forecast = {
        "location": city,
        "five_day_forecast": weather_forecast
    }

print(forecast)
    