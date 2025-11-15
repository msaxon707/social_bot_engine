import os
import json
from pathlib import Path
from openai import OpenAI

from .utils import load_json, log, BASE_DIR

# Create OpenAI client from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_style_text(style_key: str | None):
    """
    Look up the text style from config/styles.json using the style_key.
    Falls back to the default style if not found.
    """
    config = load_json(BASE_DIR / "config" / "master_settings.json")
    styles = load_json(BASE_DIR / "config" / "styles.json")

    key = style_key or config.get("default_style_key", "default")
    style_cfg = styles.get(key, styles.get("default"))
    return style_cfg.get("text_style", "friendly, simple, helpful")


def generate_post(topic: str, style_key: str | None = None):
    """
    Generate a social-media post (title, description, hashtags) for a topic.
    Uses chat.completions so it works with your OpenAI library version.
    """
    settings = load_json(BASE_DIR / "config" / "master_settings.json")
    model = settings.get("openai_model", "gpt-4.1-mini")
    text_style = get_style_text(style_key)

    prompt = f"""
You are generating SOCIAL MEDIA content.

Topic: {topic}
Style: {text_style}

You MUST respond with ONLY a single JSON object, no explanation, like:

{{
  "title": "Short clickable title",
  "description": "2–4 sentences, keyword-rich.",
  "hashtags": ["tag1", "tag2", "tag3"]
}}

Rules:
- "title": short & clickable, max {settings["max_title_length"]} characters
- "description": 2–4 sentences, helpful, keyword-rich
- "hashtags": 8–15 items, no "#" characters in the strings
- Do NOT include any text before or after the JSON.
"""

    log(f"[POST_GENERATOR] Generating content for topic: {topic}")

    # ---- Call OpenAI using chat completions (stable across versions) ----
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only returns valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as e:
        log(f"[POST_GENERATOR] ERROR calling OpenAI: {e}")
        return None

    # Extract the text from the first choice
    try:
        raw = response.choices[0].message.content
    except Exception as e:
        log(f"[POST_GENERATOR] ERROR: Could not extract message content: {e}")
        log(f"[POST_GENERATOR] Raw response object: {response}")
        return None

    # Parse JSON
    try:
        data = json.loads(raw)
    except Exception:
        log("[POST_GENERATOR] ERROR: Model returned invalid JSON.")
        log(f"[POST_GENERATOR] RAW OUTPUT:\n{raw}")
        return None

    # Normalize hashtags to include "#"
    tags = data.get("hashtags", [])
    tags = ["#" + tag.lstrip("#") for tag in tags]

    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "hashtags": tags,
    }
