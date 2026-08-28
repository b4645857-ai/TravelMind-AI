from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import json
import uuid
from pathlib import Path

from llm.parse_constraints import parse_constraints


app = FastAPI(title="TravelMind API")


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class TripRequest(BaseModel):
    text: str
    travel_date: Optional[str] = None
    return_date: Optional[str] = None
    trip_type: str = "round-trip"


class AdaptRequest(BaseModel):
    trip: dict
    change: str


class SaveRequest(BaseModel):
    trip: dict


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return FileResponse("frontend/index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    return {
        "ok": True,
        "service": "TravelMind API"
    }


# ============================================================
# DEMO DATA ENGINE
#
# This keeps the application working even if an external
# travel-data API is not connected yet.
#
# IMPORTANT:
# These are ESTIMATES, not claims of live prices.
# ============================================================

CITY_DATA = {

    "goa": {
        "best_month": "November to February",
        "weather": {
            "temperature_max": 30,
            "condition": "Warm, mostly pleasant",
            "rain_chance": 10,
            "source": "Seasonal estimate"
        },
        "places": [
            {
                "name": "Baga Beach",
                "category": "Beach",
                "rating": 4.4,
                "cost": 0,
                "description": "Popular North Goa beach with cafés, water activities and nightlife.",
                "image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2"
            },
            {
                "name": "Fort Aguada",
                "category": "History",
                "rating": 4.5,
                "cost": 50,
                "description": "Historic Portuguese fort overlooking the Arabian Sea.",
                "image": "https://images.unsplash.com/photo-1587474260584-136574528ed5"
            },
            {
                "name": "Basilica of Bom Jesus",
                "category": "Culture",
                "rating": 4.5,
                "cost": 0,
                "description": "Historic Old Goa landmark and major cultural attraction.",
                "image": "https://images.unsplash.com/photo-1596402184320-417e7178b2cd"
            },
            {
                "name": "Dudhsagar Falls",
                "category": "Nature",
                "rating": 4.6,
                "cost": 1500,
                "description": "Spectacular waterfall experience surrounded by Western Ghats.",
                "image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa"
            },
            {
                "name": "Panaji",
                "category": "Culture",
                "rating": 4.4,
                "cost": 0,
                "description": "Colourful capital city known for heritage streets and Portuguese architecture.",
                "image": "https://images.unsplash.com/photo-1596178060810-72f53ce9a65c"
            },
            {
                "name": "Palolem Beach",
                "category": "Beach",
                "rating": 4.6,
                "cost": 0,
                "description": "Relaxed South Goa beach ideal for a slower day.",
                "image": "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57"
            }
        ]
    },


    "chennai": {
        "best_month": "November to February",
        "weather": {
            "temperature_max": 29,
            "condition": "Warm and humid",
            "rain_chance": 25,
            "source": "Seasonal estimate"
        },
        "places": [
            {
                "name": "Marina Beach",
                "category": "Beach",
                "rating": 4.3,
                "cost": 0,
                "description": "One of India's most famous urban beaches.",
                "image": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220"
            },
            {
                "name": "Kapaleeshwarar Temple",
                "category": "Temple",
                "rating": 4.6,
                "cost": 0,
                "description": "Historic Dravidian temple in Mylapore.",
                "image": "https://images.unsplash.com/photo-1602427840394-0f7b4d5a2b70"
            },
            {
                "name": "Fort St. George",
                "category": "History",
                "rating": 4.2,
                "cost": 30,
                "description": "Historic colonial fort and museum complex.",
                "image": "https://images.unsplash.com/photo-1595658658481-d53d3f999875"
            },
            {
                "name": "Government Museum",
                "category": "Museum",
                "rating": 4.4,
                "cost": 15,
                "description": "Major museum complex featuring archaeology and art.",
                "image": "https://images.unsplash.com/photo-1564399579883-451a5d44ec08"
            }
        ]
    },


    "mumbai": {
        "best_month": "October to February",
        "weather": {
            "temperature_max": 30,
            "condition": "Warm and comparatively dry",
            "rain_chance": 12,
            "source": "Seasonal estimate"
        },
        "places": [
            {
                "name": "Gateway of India",
                "category": "History",
                "rating": 4.6,
                "cost": 0,
                "description": "Iconic Mumbai waterfront landmark.",
                "image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f"
            },
            {
                "name": "Marine Drive",
                "category": "Nature",
                "rating": 4.6,
                "cost": 0,
                "description": "Famous seaside promenade and sunset viewpoint.",
                "image": "https://images.unsplash.com/photo-1595658658481-d53d3f999875"
            },
            {
                "name": "Chhatrapati Shivaji Maharaj Terminus",
                "category": "Architecture",
                "rating": 4.5,
                "cost": 0,
                "description": "UNESCO-listed railway architecture landmark.",
                "image": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66"
            },
            {
                "name": "Colaba Causeway",
                "category": "Shopping",
                "rating": 4.3,
                "cost": 0,
                "description": "Popular market and shopping district.",
                "image": "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7"
            }
        ]
    }
}


# ============================================================
# RESTAURANTS / FOOD ESTIMATES
# ============================================================

FOOD_DATA = {

    "goa": [
        {
            "name": "Local Goan Breakfast",
            "meal": "Breakfast",
            "cost": 180,
            "description": "Local breakfast with regional flavours."
        },
        {
            "name": "Goan Fish Thali",
            "meal": "Lunch",
            "cost": 350,
            "description": "Traditional seafood thali."
        },
        {
            "name": "Goan Dinner",
            "meal": "Dinner",
            "cost": 450,
            "description": "Regional dinner with Goan specialities."
        }
    ],

    "chennai": [
        {
            "name": "South Indian Breakfast",
            "meal": "Breakfast",
            "cost": 120,
            "description": "Idli, dosa, vada and filter coffee."
        },
        {
            "name": "Tamil Lunch",
            "meal": "Lunch",
            "cost": 220,
            "description": "Traditional South Indian meals."
        },
        {
            "name": "Chennai Dinner",
            "meal": "Dinner",
            "cost": 300,
            "description": "Popular local dinner options."
        }
    ],

    "mumbai": [
        {
            "name": "Mumbai Breakfast",
            "meal": "Breakfast",
            "cost": 150,
            "description": "Local breakfast and tea."
        },
        {
            "name": "Mumbai Thali",
            "meal": "Lunch",
            "cost": 280,
            "description": "Regional Indian thali."
        },
        {
            "name": "Mumbai Dinner",
            "meal": "Dinner",
            "cost": 400,
            "description": "Popular local dinner options."
        }
    ]
}


# ============================================================
# HOTEL ESTIMATES
# ============================================================

HOTELS = {

    "goa": [
        {
            "name": "Budget Beach Stay",
            "tier": "Cheapest",
            "area": "North Goa",
            "nightly": 1800,
            "rating": 4.1,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"
        },
        {
            "name": "Heritage Boutique Stay",
            "tier": "Popular",
            "area": "Panaji",
            "nightly": 3200,
            "rating": 4.4,
            "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b"
        },
        {
            "name": "Premium Beach Resort",
            "tier": "Premium",
            "area": "South Goa",
            "nightly": 4500,
            "rating": 4.6,
            "image": "https://images.unsplash.com/photo-1564501049412-61c2a3083791"
        }
    ],

    "chennai": [
        {
            "name": "Budget City Stay",
            "tier": "Cheapest",
            "area": "Central Chennai",
            "nightly": 1400,
            "rating": 4.0,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"
        },
        {
            "name": "Popular City Hotel",
            "tier": "Popular",
            "area": "T Nagar",
            "nightly": 2600,
            "rating": 4.3,
            "image": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7"
        },
        {
            "name": "Premium Chennai Stay",
            "tier": "Premium",
            "area": "Adyar",
            "nightly": 4200,
            "rating": 4.6,
            "image": "https://images.unsplash.com/photo-1564501049412-61c2a3083791"
        }
    ],

    "mumbai": [
        {
            "name": "Budget Mumbai Stay",
            "tier": "Cheapest",
            "area": "Andheri",
            "nightly": 1800,
            "rating": 4.0,
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"
        },
        {
            "name": "Popular Mumbai Hotel",
            "tier": "Popular",
            "area": "Colaba",
            "nightly": 3500,
            "rating": 4.4,
            "image": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b"
        },
        {
            "name": "Premium Mumbai Hotel",
            "tier": "Premium",
            "area": "Marine Drive",
            "nightly": 5200,
            "rating": 4.7,
            "image": "https://images.unsplash.com/photo-1564501049412-61c2a3083791"
        }
    ]
}


# ============================================================
# TRANSPORT ESTIMATES
# ============================================================

ROUTES = {

    ("chennai", "goa"): {
        "flight": 5500,
        "train": 1400,
        "bus": 1300
    },

    ("goa", "chennai"): {
        "flight": 5500,
        "train": 1400,
        "bus": 1300
    },

    ("chennai", "mumbai"): {
        "flight": 5000,
        "train": 1600,
        "bus": 1800
    },

    ("mumbai", "chennai"): {
        "flight": 5000,
        "train": 1600,
        "bus": 1800
    }
}


# ============================================================
# INTERCITY TRANSPORT
# ============================================================

def build_transport(
    origin,
    destination,
    group_size,
    trip_type
):

    key = (
        origin.lower(),
        destination.lower()
    )

    route = ROUTES.get(
        key,
        {
            "flight": 6000,
            "train": 1800,
            "bus": 1500
        }
    )

    multiplier = 2 if trip_type == "round-trip" else 1

    return [

        {
            "mode": "Flight",
            "icon": "✈",
            "label": "FASTEST",
            "estimated_total":
                route["flight"]
                * group_size
                * multiplier,
            "duration": "Fastest",
            "price_type": "Estimated"
        },

        {
            "mode": "Train",
            "icon": "🚆",
            "label": "CHEAPEST",
            "estimated_total":
                route["train"]
                * group_size
                * multiplier,
            "duration": "Best value",
            "price_type": "Estimated"
        },

        {
            "mode": "Bus",
            "icon": "🚌",
            "label": "BUDGET",
            "estimated_total":
                route["bus"]
                * group_size
                * multiplier,
            "duration": "Budget option",
            "price_type": "Estimated"
        }
    ]


# ============================================================
# BUDGET ENGINE
# ============================================================

def calculate_budget(
    budget,
    days,
    group_size,
    destination,
    transport,
    trip_type
):

    city = destination.lower()

    hotel_options = HOTELS.get(
        city,
        HOTELS["chennai"]
    )

    # Always choose the cheapest hotel for the
    # initial calculated plan.
    cheapest_hotel = min(
        hotel_options,
        key=lambda x: x["nightly"]
    )

    nights = max(days - 1, 1)

    stay = (
        cheapest_hotel["nightly"]
        * nights
    )

    # Conservative meal estimate.
    food_per_person_day = {

        "goa": 850,
        "chennai": 600,
        "mumbai": 800

    }.get(city, 700)

    food = (
        food_per_person_day
        * group_size
        * days
    )

    # Local transport.
    local_transport = (
        350
        * group_size
        * days
    )

    # Activities.
    activities = (
        500
        * group_size
        * days
    )

    selected_transport = min(
        transport,
        key=lambda x:
        x["estimated_total"]
    )

    intercity = (
        selected_transport["estimated_total"]
    )

    raw_total = (
        stay
        + food
        + activities
        + local_transport
        + intercity
    )

    # ========================================================
    # IMPORTANT:
    # Estimated total MUST NOT exceed user's budget.
    #
    # If the first estimate is too high, scale flexible
    # categories down instead of lying about the budget.
    # ========================================================

    if raw_total > budget:

        fixed_transport = intercity

        remaining = max(
            budget - fixed_transport,
            0
        )

        flexible_total = (
            stay
            + food
            + activities
            + local_transport
        )

        if flexible_total > 0:

            scale = (
                remaining /
                flexible_total
            )

        else:

            scale = 0

        stay = int(stay * scale)

        food = int(food * scale)

        activities = int(
            activities * scale
        )

        local_transport = int(
            local_transport * scale
        )

    estimated_total = (
        stay
        + food
        + activities
        + local_transport
        + intercity
    )

    estimated_total = min(
        estimated_total,
        budget
    )

    per_person = int(
        estimated_total /
        max(group_size, 1)
    )

    fit_percent = int(
        (
            estimated_total /
            max(budget, 1)
        ) * 100
    )

    return {

        "budget": budget,

        "estimated_total":
            estimated_total,

        "per_person":
            per_person,

        "fit_percent":
            fit_percent,

        "categories": {

            "stay":
                stay,

            "food":
                food,

            "activities":
                activities,

            "transport":
                intercity,

            "local_transport":
                local_transport
        },

        "selected_transport":
            selected_transport,

        "selected_hotel":
            cheapest_hotel
    }


# ============================================================
# ITINERARY ENGINE
# ============================================================

def build_itinerary(
    destination,
    days,
    group_size,
    interests
):

    city = destination.lower()

    places = CITY_DATA.get(
        city,
        CITY_DATA["chennai"]
    )["places"]

    foods = FOOD_DATA.get(
        city,
        FOOD_DATA["chennai"]
    )

    itinerary = []

    for day_number in range(
        1,
        days + 1
    ):

        if day_number == 1:

            title = (
                f"Arrival & "
                f"{destination}"
            )

        elif day_number == days:

            title = (
                "Final morning & departure"
            )

        else:

            title = (
                f"Explore {destination}"
            )

        day_items = []


        # ----------------------------------------------------
        # BREAKFAST
        # ----------------------------------------------------

        breakfast = foods[0]

        day_items.append({

            "time": "08:00",

            "type": "food",

            "category": "Breakfast",

            "name":
                breakfast["name"],

            "description":
                breakfast["description"],

            "cost":
                breakfast["cost"]
                * group_size
        })


        # ----------------------------------------------------
        # MORNING PLACE
        # ----------------------------------------------------

        place_index = (
            (day_number - 1)
            % len(places)
        )

        morning_place = places[place_index]

        day_items.append({

            "time": "10:00",

            "type": "place",

            "category":
                morning_place["category"],

            "name":
                morning_place["name"],

            "description":
                morning_place["description"],

            "rating":
                morning_place["rating"],

            "cost":
                morning_place["cost"]
                * group_size
        })


        # ----------------------------------------------------
        # LUNCH
        # ----------------------------------------------------

        lunch = foods[1]

        day_items.append({

            "time": "13:00",

            "type": "food",

            "category": "Lunch",

            "name":
                lunch["name"],

            "description":
                lunch["description"],

            "cost":
                lunch["cost"]
                * group_size
        })


        # ----------------------------------------------------
        # AFTERNOON
        # ----------------------------------------------------

        afternoon_index = (
            day_number
            % len(places)
        )

        afternoon_place = places[afternoon_index]

        day_items.append({

            "time": "15:30",

            "type": "place",

            "category":
                afternoon_place["category"],

            "name":
                afternoon_place["name"],

            "description":
                afternoon_place["description"],

            "rating":
                afternoon_place["rating"],

            "cost":
                afternoon_place["cost"]
                * group_size
        })


        # ----------------------------------------------------
        # DINNER
        # ----------------------------------------------------

        dinner = foods[2]

        day_items.append({

            "time": "19:30",

            "type": "food",

            "category": "Dinner",

            "name":
                dinner["name"],

            "description":
                dinner["description"],

            "cost":
                dinner["cost"]
                * group_size
        })


        itinerary.append({

            "day":
                day_number,

            "title":
                title,

            "items":
                day_items
        })


    return itinerary


# ============================================================
# RECOMMENDATIONS
# ============================================================

def recommendations(
    destination,
    interests
):

    city = destination.lower()

    places = CITY_DATA.get(
        city,
        CITY_DATA["chennai"]
    )["places"]

    return places[:6]

# ============================================================
# BUILD TRIP
# ============================================================

@app.post("/api/plan-trip")
def plan_trip(request: TripRequest):
    parsed = parse_constraints(request.text)

    if not parsed.get("ok"):
        return {
            "ok": False,
            "data": None,
            "error": parsed.get("error", "Unable to understand trip.")
        }

    data = parsed["data"]

    origin = data.get("origin") or "Chennai"
    destination = data.get("destination") or "Goa"
    days = int(data.get("days") or 5)
    budget = int(data.get("budget_inr") or 60000)
    group_size = int(data.get("group_size") or 1)
    interests = data.get("interests", [])

    destination_key = destination.lower()

    city = CITY_DATA.get(
        destination_key,
        CITY_DATA["chennai"]
    )

    transport = build_transport(
        origin,
        destination,
        group_size,
        request.trip_type
    )

    budget_data = calculate_budget(
        budget,
        days,
        group_size,
        destination,
        transport,
        request.trip_type
    )

    itinerary = build_itinerary(
        destination,
        days,
        group_size,
        interests
    )

    result = {
        "origin": origin,
        "destination": destination,
        "days": days,
        "budget": budget_data,
        "group_size": group_size,
        "pace": data.get("pace", "Balanced"),
        "travel_persona": data.get(
            "travel_persona",
            "Balanced Explorer"
        ),
        "interests": interests,
        "month": data.get("month"),
        "travel_date": request.travel_date,
        "return_date": request.return_date,
        "trip_type": request.trip_type,
        "best_month": city["best_month"],
        "season_status": (
            "Good period to travel"
            if request.travel_date
            else "Choose a departure date to personalise this recommendation."
        ),
        "weather": city["weather"],
        "itinerary": itinerary,
        "recommendations": recommendations(
            destination,
            interests
        ),
        "transport": transport,
        "selected_transport": budget_data["selected_transport"],
        "hotels": HOTELS.get(
            destination_key,
            HOTELS["chennai"]
        ),
        "selected_hotel": budget_data["selected_hotel"]
    }

    return {
        "ok": True,
        "data": result,
        "error": None
    }


# ============================================================
# ADAPT TRIP
# ============================================================

@app.post("/api/adapt-trip")
def adapt_trip(request: AdaptRequest):
    trip = request.trip.copy()
    change = request.change.lower()

    budget_data_old = trip.get("budget", {})
    budget = int(
        budget_data_old.get("budget", 60000)
    )

    if "budget" in change or "₹" in change or "rs" in change:
        import re

        numbers = re.findall(r"\d[\d,]*", change)

        if numbers:
            try:
                budget = int(
                    numbers[-1].replace(",", "")
                )
            except ValueError:
                pass

    days = int(trip.get("days", 5))
    group_size = int(trip.get("group_size", 1))
    destination = trip.get("destination", "Goa")
    origin = trip.get("origin", "Chennai")
    trip_type = trip.get("trip_type", "round-trip")

    transport = build_transport(
        origin,
        destination,
        group_size,
        trip_type
    )

    budget_data = calculate_budget(
        budget,
        days,
        group_size,
        destination,
        transport,
        trip_type
    )

    trip["budget"] = budget_data
    trip["transport"] = transport
    trip["selected_transport"] = budget_data["selected_transport"]
    trip["selected_hotel"] = budget_data["selected_hotel"]
    trip["hotels"] = HOTELS.get(
        destination.lower(),
        HOTELS["chennai"]
    )

    return {
        "ok": True,
        "data": trip,
        "error": None
    }


# ============================================================
# SAVE TRIP
# ============================================================

@app.post("/api/save-trip")
def save_trip(request: SaveRequest):
    save_directory = Path("saved_trips")
    save_directory.mkdir(exist_ok=True)

    trip_id = str(uuid.uuid4())[:8]
    file_path = save_directory / f"{trip_id}.json"

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            request.trip,
            file,
            indent=2,
            ensure_ascii=False
        )

    return {
        "ok": True,
        "trip_id": trip_id,
        "message": "Trip saved successfully."
    }


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
