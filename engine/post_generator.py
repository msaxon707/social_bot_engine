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

    Return ONLY valid JSON with:
      "title": short, clickable, max {settings["max_title_length"]} chars
      "description": 2–4 sentence helpful text
      "hashtags": list of 8–15 keyword hashtags (no # sign)
    """

    log(f"[POST_GENERATOR] Generating content for topic: {topic}")

    try:
        response = client.responses.create(
            model=model,
            input=prompt
        )
    except Exception as e:
        log(f"[POST_GENERATOR] API ERROR: {e}")
        return None

    # Extract text safely
    try:
        raw = response.output[0].content[0].text
    except Exception as e:
        log(f"[POST_GENERATOR] ERROR reading response: {e}")
        log(f"[RAW RESPONSE] {response}")
        return None

    # Parse JSON safely
    try:
        data = json.loads(raw)
    except Exception:
        log("[POST_GENERATOR] ERROR: Model returned invalid JSON.")
        log(f"[RAW OUTPUT]: {raw}")
        return None

    hashtags = data.get("hashtags", [])
    hashtags = [f"#{tag.lstrip('#')}" for tag in hashtags]

    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "hashtags": hashtags
    }
