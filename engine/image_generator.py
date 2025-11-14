# engine/image_generator.py

import os
import base64
from datetime import datetime
from pathlib import Path
from openai import OpenAI

from .utils import BASE_DIR, ensure_dir, log

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image_for_post(account_name: str, topic: str, post: dict, style: str | None = None) -> Path | None:
    """
    Generate a Pinterest-style vertical image for a post and save it to disk.

    Returns the Path to the saved image, or None if something failed.
    """
    try:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        # Folder: /generated/<account>/<date>/
        out_dir = BASE_DIR / "generated" / account_name / date_str
        ensure_dir(out_dir)

        img_path = out_dir / f"{time_str}_image.png"

        title = post.get("title", topic)
        description = post.get("description", "")

        prompt = f"""
        Create a high-quality vertical 2:3 ratio image for Pinterest.
        Style: {style or "simple, clean, country / outdoors aesthetic"}.
        This is for a social media post.

        Post title: "{title}"
        Topic: "{topic}"
        Description summary: "{description[:200]}"
        
        Do NOT include any text on the image. Just a nice background / scene
        that matches the vibe of the title.
        """

        log(f"[{account_name}] Generating image for topic: {topic}")

        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1536",  # vertical 2:3 aspect ratio (works well for Pinterest)
            n=1
        )

        b64_data = response.data[0].b64_json
        img_bytes = base64.b64decode(b64_data)

        with open(img_path, "wb") as f:
            f.write(img_bytes)

        log(f"[{account_name}] Image saved: {img_path}")
        return img_path

    except Exception as e:
        log(f"[{account_name}] Image generation FAILED for topic '{topic}': {e}")
        return None