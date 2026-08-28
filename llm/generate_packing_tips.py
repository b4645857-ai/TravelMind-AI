"""
generate_packing_tips.py — Person B, feature #7 (part 2).
"""

from llm.llm_client import call_llm


def generate_packing_tips(destination: str, month: str, interests: list, weather_summary: str = "") -> dict:
    """
    Returns:
        { "ok": bool, "tips": list[str], "error": str | None }
    """
    system = """Output ONLY a JSON object: {"tips": ["...", "...", ...]}
Give 4-6 concise, practical packing tips (each under 12 words). No markdown, no preamble."""

    prompt = (
        f"Destination: {destination}. Month: {month or 'unspecified'}. "
        f"Interests: {interests}. Weather context: {weather_summary or 'unknown'}."
    )

    result = call_llm(prompt=prompt, system=system, max_tokens=300, expect_json=True)

    if not result["ok"]:
        return {
            "ok": True,
            "tips": [
                "Comfortable walking shoes",
                "Reusable water bottle",
                "Light cotton clothing",
                "Power bank for your phone",
            ],
            "error": result["error"],
        }

    return {"ok": True, "tips": result["json"].get("tips", []), "error": None}


if __name__ == "__main__":
    print(generate_packing_tips("Chennai", "December", ["temples", "food"]))
