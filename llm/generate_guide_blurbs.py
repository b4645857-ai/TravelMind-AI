"""
generate_guide_blurbs.py — Person B, feature #7 (part 1).

Generates a short, friendly explanation for why each scheduled stop was
included / what to expect there. Takes the optimizer's final itinerary
(list of places) and the user's interests as context.
"""

from llm.llm_client import call_llm


def generate_guide_blurbs(scheduled_places: list, interests: list) -> dict:
    """
    scheduled_places: list of place dicts (from places.json) that made the final itinerary.
    interests: the user's stated interests, used to personalize tone.

    Returns:
        { "ok": bool, "blurbs": {place_id: blurb_text}, "error": str | None }
    """
    if not scheduled_places:
        return {"ok": True, "blurbs": {}, "error": None}

    place_summaries = "\n".join(
        f"- id: {p['id']}, name: {p['name']}, category: {p['category']}, "
        f"seed: {p.get('description_seed', '')}"
        for p in scheduled_places
    )

    system = """You write short, upbeat 1-2 sentence blurbs for each travel stop.
Output ONLY a JSON object mapping place id -> blurb string. No markdown, no preamble.
Keep each blurb under 30 words. Make it feel personal to the traveler's interests."""

    prompt = f"Traveler interests: {interests}\n\nStops:\n{place_summaries}"

    result = call_llm(prompt=prompt, system=system, max_tokens=800, expect_json=True)

    if not result["ok"]:
        # Fallback: use the raw description_seed so the UI never shows a blank blurb
        fallback = {p["id"]: p.get("description_seed", p["name"]) for p in scheduled_places}
        return {"ok": True, "blurbs": fallback, "error": result["error"]}

    return {"ok": True, "blurbs": result["json"], "error": None}


if __name__ == "__main__":
    sample = [
        {"id": "kapaleeshwarar_temple", "name": "Kapaleeshwarar Temple",
         "category": "temple", "description_seed": "Ancient Dravidian temple."}
    ]
    print(generate_guide_blurbs(sample, ["temples"]))
