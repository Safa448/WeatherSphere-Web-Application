from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta, timezone
import requests

app = Flask(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/"
API_KEY = "c78dd9be1f725a6c8e7f62cf62801db1"


def tempConverter(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return round(celsius, 2), round(fahrenheit, 2)


# ------------------------
# CURRENT WEATHER ENDPOINT
# ------------------------
@app.route("/current_weather")
def current_weather():
    city = request.args.get("city", "Jeddah")

    url = BASE_URL + "weather"
    params = {"appid": API_KEY, "q": city}
    data = requests.get(url, params=params).json()

    if data.get("cod") != 200:
        return jsonify({"error": data.get("message")}), 400

    temp_c, temp_f = tempConverter(data["main"]["temp"])
    feels_c, feels_f = tempConverter(data["main"]["feels_like"])

    sunrise_local = datetime.fromtimestamp(
        data["sys"]["sunrise"], tz=timezone.utc
    ) + timedelta(seconds=data["timezone"])

    sunset_local = datetime.fromtimestamp(
        data["sys"]["sunset"], tz=timezone.utc
    ) + timedelta(seconds=data["timezone"])

    return jsonify({
        "city": city,
        "description": data["weather"][0]["description"],
        "temp_c": temp_c,
        "temp_f": temp_f,
        "feels_c": feels_c,
        "feels_f": feels_f,
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "sunrise": sunrise_local.strftime("%H:%M"),
        "sunset": sunset_local.strftime("%H:%M")
    })


# ---------------
# FORECAST ROUTE
# ---------------
@app.route("/forecast")
def forecast():
    city = request.args.get("city", "Jeddah")

    url = BASE_URL + "forecast"
    params = {"appid": API_KEY, "q": city}
    data = requests.get(url, params=params).json()

    return jsonify(data)


# ------------------------
# AIR POLLUTION ROUTE
# ------------------------
@app.route("/pollution")
def pollution():
    city = request.args.get("city", "Jeddah")

    coord_res = requests.get(
        BASE_URL + "weather", params={"appid": API_KEY, "q": city}
    ).json()

    lat = coord_res["coord"]["lat"]
    lon = coord_res["coord"]["lon"]

    url = BASE_URL + "air_pollution"
    params = {"appid": API_KEY, "lat": lat, "lon": lon}
    data = requests.get(url, params=params).json()

    return jsonify(data)



@app.route("/")
def home_page():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
