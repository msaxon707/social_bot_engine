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

    Return a JSON object with:
      - title: short, clickable, max {settings["max_title_length"]} characters
      - description: helpful, keyword-rich, 2–4 sentences
      - hashtags: a list of 8–15 relevant hashtags (without # in the strings)
    """

    log(f"[POST_GENERATOR] Generating content for topic: {topic}")

    response = client.responses.create(
        model=model,
        input=prompt,
        response_format={"type": "json_object"}
    )

    content = response.output[0].content[0].text
    data = json.loads(content)

    # Normalize hashtags to include leading '#'
    tags = data.get("hashtags", [])
    tags = [f"#{tag.lstrip('#')}" for tag in tags]

    return {
        "title": data.get("title"),
        "description": data.get("description"),
        "hashtags": tags
    }