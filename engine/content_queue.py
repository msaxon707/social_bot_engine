# engine/content_queue.py

import json
from datetime import datetime
from pathlib import Path
from .utils import BASE_DIR, ensure_dir, log

def save_post_to_queue(
    account_name: str,
    topic: str,
    post: dict,
    image_path: Path | None = None
) -> Path:
    """
    Save a generated post (and optional image) to the local content queue.

    Folder structure:
      /generated/<account_name>/<YYYY-MM-DD>/<HHMMSS>.json
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M%S")

    base_dir = BASE_DIR / "generated" / account_name / date_str
    ensure_dir(base_dir)

    file_path = base_dir / f"{time_str}.json"

    payload = {
        "account": account_name,
        "topic": topic,
        "generated_at": now.isoformat(timespec="seconds"),
        "title": post.get("title"),
        "description": post.get("description"),
        "hashtags": post.get("hashtags", []),
        "status": "ready",          # later: scheduled / posted
        "platforms": [],            # later: ["pinterest", "instagram", ...]
        "image_path": str(image_path) if image_path else None
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    log(f"[{account_name}] Saved post to queue: {file_path}")
    return file_path