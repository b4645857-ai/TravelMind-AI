"""
recommend_destination.py — Person B, feature #2.

If the user didn't specify a destination, the LLM suggests one — but it
MUST be mapped to a city we actually have curated data for (see
AVAILABLE_CITIES). This avoids ever recommending a city we can't build
a real itinerary for.
"""

from llm.llm_client import call_llm

# IMPORTANT: keep this list in sync with the keys inside data/places.json
AVAILABLE_CITIES = ["chennai"]  # add more as Person A builds out data, e.g. "jaipur"


def recommend_destination(interests: list, budget_inr: int, days: int, month: str = None) -> dict:
    """
    Suggests a destination from AVAILABLE_CITIES based on user interests/budget.

    Returns:
        { "ok": bool, "city": str | None, "reason": str | None, "error": str | None }
    """
    system = f"""You are a travel recommender restricted to ONLY these cities: {AVAILABLE_CITIES}.
You must pick exactly one city from that list — never suggest a city outside it,
even if another city would objectively fit better.

Output ONLY JSON: {{"city": "<one of the allowed cities, lowercase>", "reason": "<one short sentence>"}}
"""

    prompt = (
        f"Traveler interests: {interests}. Budget: ₹{budget_inr}. "
        f"Trip length: {days} days. Month: {month or 'unspecified'}. "
        f"Pick the best matching city from the allowed list."
    )

    result = call_llm(prompt=prompt, system=system, max_tokens=150, expect_json=True)

    if not result["ok"]:
        # Safe fallback: just pick the first available city rather than failing the demo
        return {
            "ok": True,
            "city": AVAILABLE_CITIES[0],
            "reason": "Defaulted to our best-supported city (LLM call failed).",
            "error": result["error"],
        }

    city = result["json"].get("city", "").lower()
    if city not in AVAILABLE_CITIES:
        city = AVAILABLE_CITIES[0]

    return {"ok": True, "city": city, "reason": result["json"].get("reason", ""), "error": None}


if __name__ == "__main__":
    print(recommend_destination(["temples", "food"], 8000, 3))
