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

        # Build mapping: Airtable record ID → account name
        self.account_id_map = {}  # recXXXX → pinterest_main
        self.account_name_to_id = {}  # pinterest_main → recXXXX

        accounts_raw = airtable_get("Accounts")
        for record in accounts_raw:
            record_id = record["id"]
            fields = record.get("fields", {})
            name = fields.get("Name") or fields.get("Account")
            if name:
                self.account_id_map[record_id] = name
                self.account_name_to_id[name] = record_id

    def get_all_accounts(self):
        accounts = []
        for folder in self.accounts_dir.iterdir():
            if folder.is_dir() and folder.name != "TEMPLATE_ACCOUNT":
                accounts.append(folder)
        return accounts

    def load_account_settings(self, account_path: Path, account_name: str):
        settings = load_json(account_path / "settings.json")

        topics_raw = airtable_get("Topics")
        topics = []

        for record in topics_raw:
            fields = record.get("fields", {})

            linked_accounts = fields.get("Account", [])
            if not linked_accounts:
                continue

            record_account_id = linked_accounts[0]
            mapped_name = self.account_id_map.get(record_account_id)

            if mapped_name == account_name and fields.get("Status") == "To Use":
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

        post = generate_post(topic, style_key)
        image_path = generate_image_for_post(account_name, topic, post, style_key)
        video_path = create_video_for_post(account_name, topic, post, image_path, style_key)

        queue_path = save_post_to_queue(
            account_name=account_name,
            topic=topic,
            post=post,
            image_path=image_path,
            video_path=video_path
        )

        # Convert account name → Airtable record ID
        account_record_id = self.account_name_to_id.get(account_name)

        airtable_create("Posts", {
            "Account": [account_record_id] if account_record_id else [],
            "Topic": topic,
            "Title": post.get("title"),
            "Description": post.get("description"),
            "Hashtags": ", ".join(post.get("hashtags", [])),
            "Queue Path": str(queue_path),
            "Status": "ready"
        })

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
