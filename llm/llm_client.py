"""
llm_client.py — TravelMind shared Gemini wrapper.

Handles:
- Gemini API calls
- retries
- JSON responses
- malformed JSON recovery
"""

import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_client = None


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set. Add your Gemini API key to the .env file."
            )

        _client = genai.Client(api_key=api_key)

    return _client


def _clean_json(text: str):
    """Clean common Gemini JSON formatting issues."""

    cleaned = text.strip()

    # Remove markdown fences if Gemini adds them
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    return cleaned


def call_llm(
    prompt: str,
    system: str = "",
    max_tokens: int = 1024,
    model: str = "gemini-3.6-flash",
    expect_json: bool = False,
    response_schema=None,
    max_retries: int = 2,
) -> dict:

    client = _get_client()
    last_error = None

    for attempt in range(max_retries + 1):

        try:
            full_prompt = prompt

            if system:
                full_prompt = f"{system}\n\n{prompt}"

            config_kwargs = {
                "max_output_tokens": max_tokens,
            }

            # Force Gemini to return JSON when requested
            if expect_json:
                config_kwargs["response_mime_type"] = "application/json"

                if response_schema is not None:
                    config_kwargs["response_schema"] = response_schema

            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )

            text = response.text or ""

            result = {
                "ok": True,
                "text": text,
                "json": None,
                "error": None,
            }

            if expect_json:

                cleaned = _clean_json(text)

                try:
                    result["json"] = json.loads(cleaned)
                    return result

                except json.JSONDecodeError as e:

                    # Retry with a stronger JSON instruction
                    if attempt < max_retries:

                        prompt = (
                            f"{prompt}\n\n"
                            "IMPORTANT: Your previous response was invalid JSON. "
                            "Return ONLY one complete valid JSON object. "
                            "Do not truncate it. Do not use markdown. "
                            "Do not include explanations."
                        )

                        last_error = (
                            f"Failed to parse JSON from LLM response: {e}"
                        )

                        time.sleep(1.0 * (attempt + 1))
                        continue

                    result["ok"] = False
                    result["error"] = (
                        f"Failed to parse JSON from LLM response: {e}"
                    )

                    return result

            return result

        except Exception as e:

            last_error = f"LLM error: {e}"

            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
                continue

    return {
        "ok": False,
        "text": None,
        "json": None,
        "error": last_error,
    }