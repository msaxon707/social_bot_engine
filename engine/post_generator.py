import os
import json
from pathlib import Path
from openai import OpenAI

from .utils import load_json, log, BASE_DIR

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_style_text(style_key: str | None):
    config = load_json(BASE_DIR / "config" / "master_settings.json")
    styles = load_json(BASE_DIR / "config" / "styles.json")

    key = style_key or config.get("default_style_key", "default")
    style_cfg = styles.get(key, styles.get("default"))
    return style_cfg.get("text_style", "friendly, simple, helpful")


def generate_post(topic: str, style_key: str | None = None):
    settings = load_json(BASE_DIR / "config" / "master_settings.json")
    model = settings.get("openai_model", "gpt-4.1-mini")
    text_style = get_style_text(style_key)

    prompt = f"""
You are generating SOCIAL MEDIA content.

Topic: {topic}
Style: {text_style}

Return ONLY a JSON object with:
  "title": short clickable title (max {settings["max_title_length"]} chars)
  "description": 2–4 sentences, keyword-rich
  "hashtags": array of 8–15 short strings (WITHOUT the #)
"""

    log(f"[POST_GENERATOR] Generating content for topic: {topic}")

    # --- New OpenAI JSON mode ---
    response = client.responses.create(
        model=model,
        input=prompt,
        response_format={"type": "json_object"},
    )

    # Extract the text safely
    try:
        raw = response.output[0].content[0].text
    except Exception as e:
        log(f"[POST_GENERATOR] ERROR: Could not extract text: {e}")
        log(f"[POST_GENERATOR] Raw response: {response}")
        return None

    try:
        data = json.loads(raw)
    except Exception:
        log("[POST_GENERATOR] ERROR: Model returned invalid JSON.")
        log(f"RAW OUTPUT:\n{raw}")
        return None

    # Normalize hashtags to include "#"
    tags = data.get("hashtags", [])
    tags = [f"#{tag.lstrip('#')}" for tag in tags]

    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "hashtags": tags
    }
