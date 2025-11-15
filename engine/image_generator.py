import os
import base64
from datetime import datetime
from pathlib import Path
from openai import OpenAI

from .utils import BASE_DIR, ensure_dir, log, load_json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_image_style(style_key: str | None):
    styles = load_json(BASE_DIR / "config" / "styles.json")
    key = style_key or "default"
    style_cfg = styles.get(key, styles.get("default"))
    return style_cfg.get("image_style", "clean, bright, simple background")


def generate_image_for_post(account_name: str, topic: str, post: dict, style_key: str | None = None) -> Path | None:
    try:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        out_dir = BASE_DIR / "generated" / account_name / date_str
        ensure_dir(out_dir)

        img_path = out_dir / f"{time_str}_image.png"

        title = post.get("title", topic)
        description = post.get("description", "")

        img_style = get_image_style(style_key)

        prompt = f"""
        Create a high-quality vertical image (2:3 ratio) suitable for Pinterest / social media.

        Visual style: {img_style}

        Post title: "{title}"
        Topic: "{topic}"
        Description snippet: "{description[:180]}"

        Do NOT include any text on the image.
        Just create a visually appealing background/scene that fits the topic and style.
        """

        log(f"[{account_name}] Generating image for topic: {topic}")

        response = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1536",
            n=1
        )

        b64_data = response.data[0].b64_json
        img_bytes = base64.b64decode(b64_data)

        with open(img_path, "wb") as f:
            f.write(img_bytes)

        log(f"[{account_name}] Image saved: {img_path}")
        return img_path

    except Exception as e:
        log(f"[{account_name}] Image generation FAILED for '{topic}': {e}")
        return None
