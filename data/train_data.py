"""
train_data.py — TravelMind transport engine.

Handles intercity transport estimates for:
origin -> destination

Priority:
1. Live train API when configured
2. Cached train estimate
3. Cached bus/flight estimates
4. Safe fallback when route is unknown
"""

import os
import json
import requests
from pathlib import Path

RAIL_API_KEY = os.getenv("RAIL_API_KEY", "")
RAIL_API_BASE_URL = os.getenv(
    "RAIL_API_BASE_URL",
    "https://indianrailapi.com/api/v2"
)

DATA_DIR = Path(__file__).parent
FALLBACK_FILE = DATA_DIR / "transport_estimates.json"


def _load_transport_data():
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _route_key(from_city: str, to_city: str) -> str:
    return f"{from_city.lower().strip()}_to_{to_city.lower().strip()}"


def _load_fallback(from_city: str, to_city: str) -> dict:
    data = _load_transport_data()

    route = data.get("intercity_estimated", {}).get(
        _route_key(from_city, to_city)
    )

    if not route:
        return {
            "source": "fallback_estimate",
            "from": from_city,
            "to": to_city,
            "train_inr": None,
            "bus_inr": None,
            "flight_inr": None,
            "note": "No cached transport estimate for this route."
        }

    return {
        "source": "fallback_estimate",
        "from": from_city,
        "to": to_city,
        "train_inr": route.get("train_inr"),
        "bus_inr": route.get("bus_inr"),
        "flight_inr": route.get("flight_inr"),
        "note": "Using cached transport estimates."
    }


def get_train_fare(from_city: str, to_city: str) -> dict:
    """
    Get train fare.
    Uses live API when RAIL_API_KEY is configured.
    Otherwise uses cached estimate.
    """

    if not RAIL_API_KEY:
        return _load_fallback(from_city, to_city)

    try:
        response = requests.get(
            f"{RAIL_API_BASE_URL}/TrainBetweenStation/"
            f"apikey/{RAIL_API_KEY}/"
            f"From/{from_city}/"
            f"To/{to_city}/",
            timeout=6,
        )

        response.raise_for_status()

        payload = response.json()
        trains = payload.get("Trains", [])

        if not trains:
            return _load_fallback(from_city, to_city)

        fares = []

        for train in trains:
            fare = train.get("fare_inr")

            if isinstance(fare, (int, float)) and fare > 0:
                fares.append(fare)

        cheapest = min(fares) if fares else None

        fallback = _load_fallback(from_city, to_city)

        return {
            "source": "live_api",
            "from": from_city,
            "to": to_city,
            "train_inr": cheapest,
            "bus_inr": fallback.get("bus_inr"),
            "flight_inr": fallback.get("flight_inr"),
            "num_trains_found": len(trains),
            "note": "Train fare from live API; bus/flight from estimates."
        }

    except Exception as e:
        fallback = _load_fallback(from_city, to_city)
        fallback["note"] = (
            f"Live train API failed ({e}); "
            "using cached transport estimates."
        )
        return fallback


def get_transport_options(
    from_city: str,
    to_city: str,
    group_size: int = 1,
) -> dict:
    """
    Return all available intercity transport options and
    the cheapest available option for the whole group.
    """

    result = get_train_fare(from_city, to_city)

    options = {
        "train": result.get("train_inr"),
        "bus": result.get("bus_inr"),
        "flight": result.get("flight_inr"),
    }

    valid_options = {
        name: cost
        for name, cost in options.items()
        if isinstance(cost, (int, float)) and cost > 0
    }

    if not valid_options:
        return {
            "ok": False,
            "from": from_city,
            "to": to_city,
            "options": options,
            "selected_mode": None,
            "one_way_per_person_inr": None,
            "round_trip_per_person_inr": None,
            "total_group_cost_inr": 0,
            "source": result.get("source"),
            "error": "No transport estimate available for this route."
        }

    selected_mode = min(
        valid_options,
        key=valid_options.get
    )

    one_way_per_person = valid_options[selected_mode]

    round_trip_per_person = one_way_per_person * 2

    total_group_cost = round_trip_per_person * group_size

    return {
        "ok": True,
        "from": from_city,
        "to": to_city,
        "options": options,
        "selected_mode": selected_mode,
        "one_way_per_person_inr": one_way_per_person,
        "round_trip_per_person_inr": round_trip_per_person,
        "total_group_cost_inr": total_group_cost,
        "group_size": group_size,
        "source": result.get("source"),
        "note": result.get("note"),
        "error": None,
    }


if __name__ == "__main__":
    print(
        get_transport_options(
            "Bangalore",
            "Chennai",
            group_size=2
        )
    )