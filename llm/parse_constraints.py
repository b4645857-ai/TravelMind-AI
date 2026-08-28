import re


def parse_constraints(text: str) -> dict:
    t = text.lower().strip()

    def city(pattern):
        m = re.search(pattern, t, re.I)
        return m.group(1).strip().title() if m else None

    # ---------------- Cities ----------------
    origin = city(r"from\s+([a-zA-Z]+)")
    destination = city(r"to\s+([a-zA-Z]+)")

    # ---------------- Days ----------------
    days = None

    m = re.search(r"(\d+)\s*days?", t, re.I)

    if m:
        days = int(m.group(1))
    elif re.search(r"\ba\s+week\b|\bone\s+week\b", t, re.I):
        days = 7

    # ---------------- Budget ----------------
    budget = None

    # ₹30000 / ₹30,000 / Rs 30000 / INR 30000
    m = re.search(
        r"(?:₹|rs\.?|inr)\s*([\d,]+)",
        t,
        re.I
    )

    if m:
        budget = int(m.group(1).replace(",", ""))

    # "30000 budget" / "30000 total budget"
    if budget is None:
        m = re.search(
            r"([\d,]+)\s*(?:total\s+)?budget\b",
            t,
            re.I
        )

        if m:
            budget = int(m.group(1).replace(",", ""))

    # ---------------- Group Size ----------------
    group_size = 1

    m = re.search(
        r"(\d+)\s*(?:people|persons|travelers|travellers)",
        t,
        re.I
    )

    if m:
        group_size = int(m.group(1))

    # ---------------- Pace ----------------
    if (
        "don't want to rush" in t
        or "do not want to rush" in t
        or "relaxed" in t
        or "relaxation" in t
        or "slow trip" in t
        or "slow pace" in t
    ):
        pace = "Relaxed"
        persona = "Snail"

    elif (
        "packed" in t
        or "see everything" in t
        or "as much as possible" in t
    ):
        pace = "Packed"
        persona = "Checklist Warrior"

    else:
        pace = "Balanced"
        persona = "Balanced Explorer"

    # ---------------- Interests ----------------
    interests = []

    keywords = {
        "beaches": ["beach", "beaches"],
        "food": ["food", "foodie", "local food"],
        "temples": ["temple", "temples"],
        "culture": ["culture", "cultural"],
        "nightlife": ["nightlife", "night life"],
        "history": ["history", "historical"],
        "nature": ["nature", "waterfalls", "hiking"],
        "relaxation": ["relax", "relaxation", "slow"],
    }

    for name, words in keywords.items():
        if any(word in t for word in words):
            interests.append(name)

    if not interests:
        interests = ["culture", "food"]

    # ---------------- Month ----------------
    month = None

    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]

    for month_name in months:
        if month_name in t:
            month = month_name.title()
            break

    # ---------------- Validation ----------------
    if not days:
        return {
            "ok": False,
            "data": None,
            "error": "Please specify the number of days.",
        }

    if not budget:
        return {
            "ok": False,
            "data": None,
            "error": "Please specify your budget.",
        }

    # ---------------- Final Result ----------------
    return {
        "ok": True,
        "data": {
            "origin": origin,
            "destination": destination,
            "days": days,
            "budget_inr": budget,
            "group_size": group_size,
            "pace": pace,
            "travel_persona": persona,
            "interests": interests,
            "month": month,
        },
        "error": None,
    }


if __name__ == "__main__":

    tests = [
        "5 days from Chennai to Chennai, ₹30000 total budget for 4 people, I love temples, local food, beaches and culture, I want a balanced trip with some relaxation, travelling in December",

        "5 days from Chennai to Goa, ₹60000 total budget for 4 people, I love beaches, food and nightlife",

        "3 days from Chennai to Pondicherry, ₹15000 for 2 people, I love food and beaches",

        "5 days from Bangalore to Chennai, ₹30000, 2 people, I don't want to rush",

        "A week from Mumbai to Goa, ₹60000, I want to see everything",
    ]

    for x in tests:
        print("\nINPUT:", x)
        print("OUTPUT:", parse_constraints(x))