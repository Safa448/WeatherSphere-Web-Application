
# mainV2.py
# -----------------------------------------
# This file contains all the backend logic
# for fetching and processing weather data
# from the OpenWeatherMap API.
# -----------------------------------------

from datetime import datetime, timedelta, timezone
import requests
import os

# Base API URL and API Key (stored in environment variable for security)
BASE_URL = "https://api.openweathermap.org/data/2.5/"
API_KEY = "c78dd9be1f725a6c8e7f62cf62801db1"  # os.getenv("OPENWEATHER_API_KEY")  # safer than hardcoding

# -------------------------------
# Temperature Converter
# -------------------------------
def tempConverter(kelvin):
    """Convert Kelvin to Celsius and Fahrenheit."""
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit

# -------------------------------
# Current Weather
# -------------------------------
def getCurrentWeather(city):
    """Fetch and process current weather data for a city."""
    url = BASE_URL + "weather"
    params = {"appid": API_KEY, "q": city}
    response = requests.get(url, params=params).json()

    # Debug (optional): check what weather looks like
    # print("DEBUG current.weather:", response.get("weather"))

    if response.get("cod") != 200:
        return {"error": response.get("message")}

    # Get icon code (e.g., "10d" or "01n") and build icon URL
    # OpenWeather official pattern: https://openweathermap.org/img/wn/{icon}@2x.png
    icon_code = response['weather'][0]['icon']
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    temp_c, temp_f = tempConverter(response['main']['temp'])
    feels_c, feels_f = tempConverter(response['main']['feels_like'])

    sunrise = datetime.fromtimestamp(response['sys']['sunrise'], tz=timezone.utc) + timedelta(seconds=response['timezone'])
    sunset = datetime.fromtimestamp(response['sys']['sunset'], tz=timezone.utc) + timedelta(seconds=response['timezone'])

    return {
        "city": response['name'],
        "description": response['weather'][0]['description'],
        "temp_c": temp_c,
        "temp_f": temp_f,
        "feels_c": feels_c,
        "feels_f": feels_f,
        "humidity": response['main']['humidity'],
        "wind": response['wind']['speed'],
        "sunrise": sunrise.strftime('%H:%M'),
        "sunset": sunset.strftime('%H:%M'),
        "icon": icon_code,
        "icon_url": icon_url
    }

# -------------------------------
# Forecast
# -------------------------------
def getForecast(city):
    """Fetch and process 5-day forecast data for a city."""
    url = BASE_URL + "forecast"
    params = {"appid": API_KEY, "q": city}
    response = requests.get(url, params=params).json()

    # Debug (optional): ensure we have list items
    # print("DEBUG forecast.first.weather:", response.get("list", [{}])[0].get("weather"))

    if response.get("cod") != "200":
        return {"error": response.get("message")}

    forecast_list = []
    for item in response['list']:
        temp_c, temp_f = tempConverter(item['main']['temp'])

        # Per-item icon
        icon_code = item['weather'][0]['icon']
        #print(icon_code)
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

        forecast_list.append({
            "dt_txt": item['dt_txt'],
            "description": item['weather'][0]['description'],
            "temp_c": temp_c,
            "temp_f": temp_f,
            "humidity": item['main']['humidity'],
            "icon": icon_code,
            "icon_url": icon_url
        })
    return forecast_list

# -------------------------------
# Air Pollution
# -------------------------------
def getPollution(city):
    """Fetch air pollution data for a city."""
    coord_url = BASE_URL + "weather"
    coord_params = {"appid": API_KEY, "q": city}
    coord_data = requests.get(coord_url, params=coord_params).json()

    if "coord" not in coord_data:
        return {"error": coord_data.get("message", "Could not fetch coordinates")}

    lat, lon = coord_data['coord']['lat'], coord_data['coord']['lon']
    url = BASE_URL + "air_pollution"
    params = {"appid": API_KEY, "lat": lat, "lon": lon}
    response = requests.get(url, params=params).json()

    print("")
    print("")
    print(response['list'][0]['main']['aqi'])
    print("")
    print (response['list'][0]['components'])

    return {
        "aqi": response['list'][0]['main']['aqi'],
        "components": response['list'][0]['components']
    }

# -------------------------------
# Extra Feature: Stats
# -------------------------------
def getForecastStats(city):
    """Calculate average temperature and humidity from forecast data."""
    forecast = getForecast(city)
    if isinstance(forecast, dict) and "error" in forecast:
        return forecast

    temps = [f['temp_c'] for f in forecast]
    hums = [f['humidity'] for f in forecast]

    return {
        "avg_temp": sum(temps) / len(temps),
        "avg_humidity": sum(hums) / len(hums)
    }

# -------------------------------
# Extra Feature: Compare
# -------------------------------
def compareCities(city1, city2):
    """Compare current weather between two cities."""
    data1 = getCurrentWeather(city1)
    data2 = getCurrentWeather(city2)

    return {"city1": data1, "city2": data2}
