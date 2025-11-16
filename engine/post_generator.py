import os, json, logging
from datetime import datetime
from openai import OpenAI
from .utils import load_json, BASE_DIR

log = logging.getLogger("postgen")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _style(key: str | None) -> str:
    cfg = load_json(BASE_DIR / "config" / "styles.json")
    return cfg.get(key or "default", {}).get("text_style", "friendly")

def generate_post(topic: str, style_key: str | None = None) -> dict | None:
    model = "gpt-4o-mini"
    prompt = (
        f"Generate SOCIAL MEDIA content.\n\nTopic: {topic}\n"
        f"Style: {_style(style_key)}\n\n"
        "Return JSON with keys title, description (≤3 sentences), "
        "hashtags (array 5-10, no #)."
    )
    try:
        raw = (
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            .choices[0]
            .message
            .content
        )
        data = json.loads(raw)
        data["hashtags"] = [f"#{h.lstrip('#')}" for h in data.get("hashtags", [])]
        data["generated_at"] = datetime.utcnow().isoformat()
        return data
    except Exception as e:
        log.error("OpenAI error: %s", e)
        return None
