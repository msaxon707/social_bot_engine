import os
import requests
from engine.airtable_client import airtable_get, airtable_update
from engine.utils import log

PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")

def get_ready_post():
    """Fetch one 'ready' post from Airtable."""
    recs = airtable_get("Posts?filterByFormula=Status='ready'")
    return recs[0] if recs else None


def post_to_pinterest(title: str, description: str, image_url: str):
    """Create a pin on Pinterest board."""
    url = f"https://api.pinterest.com/v5/pins"
    payload = {
        "board_id": PINTEREST_BOARD_ID,
        "title": title,
        "description": description,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }

    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code not in (200, 201):
        log(f"[Pinterest] Failed to post: {res.text}")
        return None
    return res.json()


def run_pinterest_post():
    """Main Pinterest posting flow."""
    post = get_ready_post()
    if not post:
        log("[Pinterest] No ready posts found.")
        return

    fields = post["fields"]
    title = fields.get("Title", "Untitled")
    description = fields.get("Description", "")
    hashtags = fields.get("Hashtags", "")

    # generate or use an image (placeholder example)
    image_url = "https://picsum.photos/800/600"  # temporary placeholder

    log(f"[Pinterest] Posting '{title}'...")
    pin = post_to_pinterest(title, description + "\n\n" + hashtags, image_url)
    if pin:
        airtable_update("Posts", post["id"], {"Status": "posted"})
        log(f"[Pinterest] ✅ Posted to Pinterest: {title}")
