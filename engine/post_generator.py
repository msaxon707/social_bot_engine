import os
from pathlib import Path
from openai import OpenAI
from .utils import load_json, log, BASE_DIR

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(topic: str, style: str = None):
    settings = load_json(BASE_DIR / "config" / "master_settings.json")
    model = settings.get("openai_model", "gpt-4.1-mini")

    prompt = f"""
    Create structured social media content.
    Topic: {topic}
    Style: {style or settings['default_style']}

    Return JSON with keys:
    - title (max {settings["max_title_length"]} chars)
    - description
    - hashtags (list)
    """

    response = client.responses.create(
        model=model,
        input=prompt,
        response_format={"type": "json_object"}
    )

    content = response.output[0].content[0].text

    import json
    return json.loads(content)
