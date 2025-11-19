import os
import requests
from engine.airtable_client import airtable_get, airtable_update
from engine.utils import log

# Load credentials from environment
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")

def get_ready_post():
    """Fetch the first post marked 'ready' in Airtable."""
    recs = airtable_get("Posts?filterByFormula=Status='ready'")
    if recs:
        log(f"[Pinterest] Found {len(recs)} ready post(s).")
        return recs[0]
    log("[Pinterest] No ready posts found.")
    return None


def post_to_pinterest(title: str, description: str, image_url: str):
    """Post a pin to Pinterest board."""
    url = "https://api.pinterest.com/v5/pins"
    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "board_id": PINTEREST_BOARD_ID,
        "title": title,
        "description": description,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code not in (200, 201):
        log(f"[Pinterest] ❌ Failed to post: {res.status_code} {res.text}")
        return None
    log(f"[Pinterest] ✅ Successfully created pin for: {title}")
    return res.json()


def run_pinterest_post():
    """Main Pinterest posting process."""
    post = get_ready_post()
    if not post:
        return

    fields = post["fields"]
    title = fields.get("Title", "Untitled Post")
    description = fields.get("Description", "")
    hashtags = fields.get("Hashtags", "")

    # TODO: Replace this placeholder with your generated image logic
    image_url = "https://picsum.photos/800/600"

    log(f"[Pinterest] Preparing to post: {title}")
    pin = post_to_pinterest(title, f"{description}\n\n{hashtags}", image_url)
    if pin:
        airtable_update("Posts", post["id"], {"Status": "posted"})
        log(f"[Pinterest] Marked as posted in Airtable: {title}")


if __name__ == "__main__":
    run_pinterest_post()
