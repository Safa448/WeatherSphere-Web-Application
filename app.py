
# app.py
# -----------------------------------------
# This file runs the Flask web application.
# It imports functions from mainV2.py and
# renders them into a single dashboard page.
# -----------------------------------------

from flask import Flask, render_template, request
import mainV2

app = Flask(__name__)

# Human-friendly pollutant names (for templates / display)
POLLUTANT_NAMES = {
    'co': 'Carbon monoxide (CO)',
    'no': 'Nitric oxide (NO)',
    'no2': 'Nitrogen dioxide (NO₂)',
    'o3': 'Ozone (O₃)',
    'so2': 'Sulfur dioxide (SO₂)',
    'pm2_5': 'Particulate matter PM2.5',
    'pm10': 'Particulate matter PM10',
    'nh3': 'Ammonia (NH₃)',
}

DEFAULT_CITY = "Jeddah"  # We can change this to whatever we want 

def normalize_city(value: str | None) -> str | None:
    """
    Normalize city input from query args:
    - Treat None, empty strings, and the string 'None' (any case) as missing.
    - Trim whitespace.
    - Return None if missing, otherwise the cleaned city string.
    """
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == "" or cleaned.lower() == "none":
        return None
    return cleaned


def safe_call(func, *args, **kwargs):
    """
    Call a backend function safely and return None on failure.
    Optionally you can log the error here.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # You can log this error with your preferred logger
        # print(f"[ERROR] {func.__name__} failed: {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def dashboard():
    """Main dashboard page with all features."""
    # Support both GET query params and POST form data
    if request.method == "POST":
        city_raw = request.form.get("city")
        city2_raw = request.form.get("city2")
    else:
        city_raw = request.args.get("city")
        city2_raw = request.args.get("city2")

    # Normalize inputs
    city = normalize_city(city_raw) or DEFAULT_CITY
    city2 = normalize_city(city2_raw)

    # Fetch data from backend functions (defensive: don't crash on one failure)
    current = safe_call(mainV2.getCurrentWeather, city)
    forecast = safe_call(mainV2.getForecast, city)
    pollution = safe_call(mainV2.getPollution, city)
    stats = safe_call(mainV2.getForecastStats, city)

    comparison = ""
    if city2:
        comparison = safe_call(mainV2.compareCities, city, city2) or ""

    # Units for pollution data (OpenWeather Air Pollution API typically uses µg/m³)
    units = "µg/m³"

    return render_template(
        "dashboard.html",
        city=city,
        city2=city2,
        current=current,
        forecast=forecast,
        pollution=pollution,
        stats=stats,
        comparison=comparison,
        pollutant_names=POLLUTANT_NAMES,  # for friendly names in template
        units=units,
    )


if __name__ == "__main__":
    app.run(debug=True)

