import random
from pathlib import Path

from .utils import load_json, log, BASE_DIR
from .post_generator import generate_post
from .content_queue import save_post_to_queue
from .image_generator import generate_image_for_post
from .video_generator import create_video_for_post
from .airtable_client import airtable_get, airtable_create, airtable_update


class AccountManager:
    def __init__(self):
        self.accounts_dir = BASE_DIR / "accounts"

        # Load Accounts table mapping
        self.account_id_map = {}  # record_id → account_name
        accounts_raw = airtable_get("Accounts")
        for record in accounts_raw:
            fields = record.get("fields", {})
            name = fields.get("Name") or fields.get("Account") or record["id"]
            self.account_id_map[record["id"]] = name

    def get_all_accounts(self):
        accounts = []
        for folder in self.accounts_dir.iterdir():
            if folder.is_dir() and folder.name != "TEMPLATE_ACCOUNT":
                accounts.append(folder)
        return accounts

    def load_account_settings(self, account_path: Path, account_name: str):
        settings = load_json(account_path / "settings.json")

        # --- Fetch Topics ---
        topics_raw = airtable_get("Topics")
        topics = []

        for record in topics_raw:
            fields = record.get("fields", {})

            # Airtable returns the LINKED RECORD ID
            linked_account_ids = fields.get("Account", [])

            if not linked_account_ids:
                continue

            linked_id = linked_account_ids[0]
            linked_name = self.account_id_map.get(linked_id)

            if linked_name == account_name and fields.get("Status") == "To Use":
                topics.append({
                    "topic": fields.get("Topic"),
                    "id": record["id"]
                })

        return {
            "settings": settings,
            "topics": topics
        }

    def generate_for_account(self, account_path: Path):
        account_name = account_path.name
        data = self.load_account_settings(account_path, account_name)

        settings = data["settings"]
        topics = data["topics"]

        if not topics:
            log(f"[{account_name}] No available topics in Airtable.")
            return None

        chosen = random.choice(topics)
        topic = chosen["topic"]
        topic_id = chosen["id"]

        style_key = settings.get("style_key", "default")

        log(f"[{account_name}] Generating content for topic: {topic}")

        # 1) Text
        post = generate_post(topic, style_key)

        # 2) Image
        image_path = generate_image_for_post(
            account_name=account_name,
            topic=topic,
            post=post,
            style_key=style_key
        )

        # 3) Video
        video_path = create_video_for_post(
            account_name=account_name,
            topic=topic,
            post=post,
            image_path=image_path,
            style_key=style_key
        )

        # 4) Save locally
        queue_path = save_post_to_queue(
            account_name=account_name,
            topic=topic,
            post=post,
            image_path=image_path,
            video_path=video_path
        )

        # 5) Save to Airtable Posts
        airtable_create("Posts", {
            "Account": [account_record_id],
            "Topic": topic,
            "Title": post.get("title"),
            "Description": post.get("description"),
            "Hashtags": ", ".join(post.get("hashtags", [])),
            "Queue Path": str(queue_path),
            "Status": "ready"
        })

        # 6) Mark topic used
        airtable_update("Topics", topic_id, {"Status": "Used"})

        log(f"[{account_name}] Finished generating + saving content for: {topic}")

        return {
            "account": account_name,
            "topic": topic,
            "post": post,
            "queue_path": str(queue_path),
            "image_path": str(image_path) if image_path else None,
            "video_path": str(video_path) if video_path else None
        }
