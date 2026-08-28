import json

from llm.parse_constraints import parse_constraints
from optimizer.model import solve_itinerary


# 1. Parse the user's natural-language request
user_input = "3 days in Chennai, ₹8000 budget, love temples and food"

parsed = parse_constraints(user_input)

print("\n--- PARSED CONSTRAINTS ---")
print(parsed)

if not parsed["ok"]:
    print("\nParser failed.")
    raise SystemExit(1)


# 2. Load Chennai places
with open("data/places.json", "r", encoding="utf-8") as f:
    places_data = json.load(f)

places = places_data["chennai"]


# 3. Run OR-Tools using the parsed constraints
result = solve_itinerary(
    places=places,
    days=parsed["data"]["days"],
    budget_inr=parsed["data"]["budget_inr"],
    pace=parsed["data"]["pace"],
    interests=parsed["data"]["interests"],
    group_size=parsed["data"]["group_size"],
)


# 4. Show the optimizer result
print("\n--- OPTIMIZER RESULT ---")
print(json.dumps(result, indent=2))