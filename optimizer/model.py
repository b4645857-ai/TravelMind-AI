"""
model.py — Person C's core optimizer. Feature #6.

Uses Google OR-Tools CP-SAT to schedule places into a day-by-day itinerary
that fits budget + time (pace) + interest-weighting, and reports WHY any
place was rejected.

Design notes (read before modifying):
- Each place is a 0/1 decision per day: x[place_id, day] = 1 if scheduled that day.
- A place can be scheduled on at most ONE day total (no duplicates).
- Each day has a time budget (minutes) determined by `pace`.
- Total spend (places + hotel + transport) must stay <= budget_inr.
- Objective maximizes interest-weighted "value", with a penalty for
  weather-flagged outdoor places on rainy days.
- This is a small, fast ILP — should solve in well under 1 second for
  hackathon-sized datasets (tens of places), which is what makes the
  <1-2s live re-plan feature possible.
"""

from ortools.sat.python import cp_model

# Minutes of "touring time" available per day, by pace
PACE_MINUTES = {
    "Relaxed": 240,   # ~4 hours of activities/day
    "Balanced": 360,  # ~6 hours/day
    "Packed": 540,    # ~9 hours/day
}

WEATHER_PENALTY_WEIGHT = 3  # subtracted from value if scheduled outdoor on a rainy day


def _interest_score(place: dict, interests: list) -> int:
    """Simple overlap score: how many of the user's interests this place matches."""
    place_interests = set(place.get("interests", []))
    return len(place_interests.intersection(set(interests)))


def solve_itinerary(
    places: list,
    days: int,
    budget_inr: int,
    pace: str,
    interests: list,
    group_size: int = 1,
    hotel_cost_per_night: int = 0,
    fixed_transport_cost: int = 0,
    rainy_days: set = None,
) -> dict:
    """
    Args:
        places: list of place dicts from places.json (optionally weather-annotated
                 with 'weather_penalty': bool per weather_check.filter_places_for_weather)
        days: number of trip days
        budget_inr: total trip budget (for the whole group)
        pace: "Relaxed" | "Balanced" | "Packed"
        interests: list of user interest strings
        group_size: number of travelers (affects per-person cost, not per-place cost —
                    we assume place entry costs are PER PERSON, so multiply accordingly)
        hotel_cost_per_night: nightly hotel cost for the group (or per room)
        fixed_transport_cost: total transport cost already committed (trains/flights/buses)
        rainy_days: set of day indices (0-based) that are rainy, for weather penalty

    Returns:
        {
          "ok": bool,
          "schedule": {day_index: [place_id, ...]},
          "rejected": [{"place_id": str, "reason": str}],
          "total_cost_inr": int,
          "error": str | None,
        }
    """
    rainy_days = rainy_days or set()
    minutes_per_day = PACE_MINUTES.get(pace, PACE_MINUTES["Balanced"])
    nights = max(days - 1, 0)
    hotel_total = hotel_cost_per_night * nights

    if not places:
        return {"ok": True, "schedule": {}, "rejected": [], "total_cost_inr": hotel_total + fixed_transport_cost, "error": None}

    model = cp_model.CpModel()

    # --- Decision variables ---
    x = {}
    for p in places:
        for d in range(days):
            x[(p["id"], d)] = model.NewBoolVar(f"x_{p['id']}_{d}")

    # A place can be scheduled at most once across all days
    for p in places:
        model.Add(sum(x[(p["id"], d)] for d in range(days)) <= 1)

    # --- Time constraint per day ---
    for d in range(days):
        model.Add(
            sum(x[(p["id"], d)] * p["duration_minutes"] for p in places) <= minutes_per_day
        )

    # --- Budget constraint (places cost * group_size, plus hotel + transport) ---
    # cp_model requires integer coefficients; costs are already integers (INR).
    place_cost_terms = [
        x[(p["id"], d)] * p["cost_inr"] * group_size
        for p in places
        for d in range(days)
    ]
    model.Add(sum(place_cost_terms) + hotel_total + fixed_transport_cost <= budget_inr)

    # --- Objective: maximize interest-weighted value, minus weather penalty ---
    objective_terms = []
    for p in places:
        score = _interest_score(p, interests)
        base_value = (score * 10) + 1  # +1 so even non-matching places have some value (fills gaps)
        for d in range(days):
            penalty = WEATHER_PENALTY_WEIGHT if (d in rainy_days and p.get("outdoor")) else 0
            value = max(base_value - penalty, 0)
            objective_terms.append(x[(p["id"], d)] * value)

    model.Maximize(sum(objective_terms))

    # --- Solve ---
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 3.0  # keeps live re-plan fast
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {
            "ok": False,
            "schedule": {},
            "rejected": [{"place_id": p["id"], "reason": "over_budget"} for p in places],
            "total_cost_inr": hotel_total + fixed_transport_cost,
            "error": "No feasible schedule found — budget or time constraints too tight.",
        }

    # --- Extract schedule ---
    schedule = {d: [] for d in range(days)}
    scheduled_ids = set()
    total_place_cost = 0

    for p in places:
        for d in range(days):
            if solver.Value(x[(p["id"], d)]) == 1:
                schedule[d].append(p["id"])
                scheduled_ids.add(p["id"])
                total_place_cost += p["cost_inr"] * group_size

    total_cost_inr = total_place_cost + hotel_total + fixed_transport_cost

    # --- Determine rejection reasons for unscheduled places ---
    rejected = []
    remaining_budget = budget_inr - total_cost_inr
    for p in places:
        if p["id"] in scheduled_ids:
            continue
        score = _interest_score(p, interests)
        if score == 0:
            reason = "low_interest_match"
        elif p["cost_inr"] * group_size > max(remaining_budget, 0):
            reason = "over_budget"
        else:
            # Would have fit budget-wise but no day had enough free time slots
            reason = "time_conflict"
        rejected.append({"place_id": p["id"], "reason": reason})

    return {
        "ok": True,
        "schedule": schedule,
        "rejected": rejected,
        "total_cost_inr": total_cost_inr,
        "error": None,
    }


if __name__ == "__main__":
    # Quick manual test: python -m optimizer.model
    sample_places = [
        {"id": "a", "name": "Temple", "cost_inr": 0, "duration_minutes": 90,
         "interests": ["temples"], "outdoor": True},
        {"id": "b", "name": "Museum", "cost_inr": 15, "duration_minutes": 100,
         "interests": ["history"], "outdoor": False},
        {"id": "c", "name": "Fancy Dinner", "cost_inr": 2000, "duration_minutes": 60,
         "interests": ["food"], "outdoor": False},
    ]
    result = solve_itinerary(
        places=sample_places,
        days=2,
        budget_inr=500,
        pace="Balanced",
        interests=["temples", "food"],
        group_size=1,
    )
    import json
    print(json.dumps(result, indent=2))
