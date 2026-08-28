"""
weather_check.py — feature #5.

Fetches a simple daily forecast (using Open-Meteo, which is free and needs
NO API key — great for hackathon reliability) and flags rainy days so the
optimizer can deprioritize outdoor places on those days.
"""

import requests
from datetime import datetime, timedelta

# Free, no-key-required weather API
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# lat/lon for cities we support (keep in sync with data/places.json keys)
CITY_COORDS = {
    "chennai": {"lat": 13.0827, "lon": 80.2707},
}


def get_daily_weather(city: str, num_days: int) -> dict:
    """
    Returns:
        {
          "ok": bool,
          "days": [ {"date": "2026-08-29", "rain_probability": 0-100, "is_rainy": bool}, ... ],
          "error": str | None
        }
    """
    coords = CITY_COORDS.get(city.lower())
    if not coords:
        return {"ok": False, "days": [], "error": f"No coordinates configured for city '{city}'"}

    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": "precipitation_probability_max",
                "forecast_days": min(num_days, 16),
                "timezone": "auto",
            },
            timeout=6,
        )
        resp.raise_for_status()
        payload = resp.json()

        dates = payload["daily"]["time"]
        probs = payload["daily"]["precipitation_probability_max"]

        days = [
            {
                "date": d,
                "rain_probability": p,
                "is_rainy": p is not None and p >= 60,  # threshold: 60%+ chance = rainy
            }
            for d, p in zip(dates, probs)
        ]
        return {"ok": True, "days": days, "error": None}

    except Exception as e:
        # Fallback: assume no rain so the app still runs during the demo
        fallback_days = [
            {
                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "rain_probability": None,
                "is_rainy": False,
            }
            for i in range(num_days)
        ]
        return {"ok": False, "days": fallback_days, "error": str(e)}


def filter_places_for_weather(places: list, day_is_rainy: bool) -> list:
    """
    Given a list of place dicts and whether that day is rainy, returns a
    de-prioritized-but-not-destroyed list: outdoor places get a penalty
    flag rather than being deleted outright, so the optimizer can still
    use them if nothing else fits.
    """
    result = []
    for p in places:
        p_copy = dict(p)
        p_copy["weather_penalty"] = bool(day_is_rainy and p.get("outdoor"))
        result.append(p_copy)
    return result


if __name__ == "__main__":
    print(get_daily_weather("chennai", 3))
