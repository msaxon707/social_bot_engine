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

        # Maps Airtable Account name -> Airtable record ID
        self.account_name_to_id = {}
        self.account_id_to_name = {}

        # Load Airtable Account table so we can resolve linked record IDs
        self._load_accounts_table()

    def _load_accounts_table(self):
        """
        Loads Airtable 'Accounts' table to store record IDs for linking.
        """
        records = airtable_get("Accounts")

        for record in records:
            record_id = record.get("id")
            fields = record.get("fields", {})
            name = fields.get("Name") or fields.get("Account")

            if name:
                self.account_name_to_id[name] = record_id
                self.account_id_to_name[record_id] = name

        log(f"[ACCOUNTS] Loaded {len(self.account_name_to_id)} accounts from Airtable.")

    def get_all_accounts(self):
        accounts = []
        for folder in self.accounts_dir.iterdir():
            if folder.is_dir() and folder.name != "TEMPLATE_ACCOUNT":
                accounts.append(folder)
        return accounts

    def load_account_settings(self, account_path: Path, account_name: str):
        settings = load_json(account_path / "settings.json")

        # Get topics table
        topics_raw = airtable_get("Topics")
        topics = []

        # Get Airtable Account record ID
        account_record_id = self.account_name_to_id.get(account_name)

        for record in topics_raw:
            fields = record.get("fields", {})

            linked_accounts = fields.get("Account", [])
            topic_status = fields.get("Status")

            # Only include topics for this specific account
            if linked_accounts and linked_accounts[0] == account_record_id and topic_status == "To Use":
                topics.append({
                    "topic": fields.get("Topic"),
                    "id": record.get("id")
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

        # 1) Generate post (text)
        post = generate_post(topic, style_key)

        # 2) Generate image
        image_path = generate_image_for_post(
            account_name=account_name,
            topic=topic,
            post=post,
            style_key=style_key
        )

        # 3) Generate video
        video_path = create_video_for_post(
            account_name=account_name,
            topic=topic,
            post=post,
            image_path=image_path,
            style_key=style_key
        )

        # Save locally
        queue_path = save_post_to_queue(
            account_name=account_name,
            topic=topic,
            post=post,
            image_path=image_path,
            video_path=video_path
        )

        # Airtable record ID for linked field
        account_record_id = self.account_name_to_id.get(account_name)
