# engine/account_manager.py

import random
from pathlib import Path

from .utils import load_json, log, BASE_DIR
from .post_generator import generate_post
from .content_queue import save_post_to_queue
from .image_generator import generate_image_for_post
from .airtable_client import airtable_get, airtable_create, airtable_update


class AccountManager:
    def __init__(self):
        self.accounts_dir = BASE_DIR / "accounts"

    def get_all_accounts(self):
        """Return a list of account directories, ignoring TEMPLATE_ACCOUNT."""
        accounts = []
        for folder in self.accounts_dir.iterdir():
            if folder.is_dir() and folder.name != "TEMPLATE_ACCOUNT":
                accounts.append(folder)
        return accounts

    def load_account_settings(self, account_path: Path, account_name: str):
        """
        Load settings.json + fetch topics for this account from Airtable.
        """
        settings = load_json(account_path / "settings.json")

        # Pull topics from Airtable
        topics_raw = airtable_get("Topics")
        topics = []

        for record in topics_raw:
            fields = record.get("fields", {})

            # Topic Filtering:
            # - Assigned to account
            # - Status == "To Use"
            if (
                fields.get("Account")
                and fields["Account"][0] == account_name
                and fields.get("Status") == "To Use"
            ):
                topics.append({
                    "topic": fields["Topic"],
                    "id": record["id"]
                })

        return {
            "settings": settings,
            "topics": topics
        }

    def generate_for_account(self, account_path: Path):
        """
        Generate text + image content for a single account,
        save to local queue + Airtable.
        """
        account_name = account_path.name
        data = self.load_account_settings(account_path, account_name)

        settings = data["settings"]
        topics = data["topics"]

        if not topics:
            log(f"[{account_name}] No available topics in Airtable.")
            return None

        # pick a random topic
        chosen = random.choice(topics)
        topic = chosen["topic"]
        topic_id = chosen["id"]

        style = settings.get("style")

        log(f"[{account_name}] Generating content for topic: {topic}")

        # ----------------------------
        # 1) Generate text content
        # ----------------------------
        post = generate_post(topic, style)

        # ----------------------------
        # 2) Generate image
        # ----------------------------
        image_path = generate_image_for_post(
            account_name=account_name,
            topic=topic,
            post=post,
            style=style
        )

        # ----------------------------
        # 3) Save content locally
        # ----------------------------
        queue_path = save_post_to_queue(
            account_name=account_name,
            topic=topic,
            post=post,
            image_path=image_path
        )

        # ----------------------------
        # 4) Save to Airtable → Posts table
        # ----------------------------
        airtable_create("Posts", {
            "Account": [account_name],
            "Topic": topic,
            "Title": post.get("title"),
            "Description": post.get("description"),
            "Hashtags": ", ".join(post.get("hashtags", [])),
            "Queue Path": str(queue_path),
            "Status": "ready",
        })

        # ----------------------------
        # 5) Mark topic as Used in Airtable
        # ----------------------------
        airtable_update("Topics", topic_id, {
            "Status": "Used"
        })

        log(f"[{account_name}] Finished generating + saving content for: {topic}")

        return {
            "account": account_name,
            "topic": topic,
            "post": post,
            "queue_path": str(queue_path),
            "image_path": str(image_path) if image_path else None
        }

    def run_all(self):
        """
        Loop through all account folders and generate content for each.
        """
        accounts = self.get_all_accounts()

        if not accounts:
            log("No account folders found in /accounts.")
            return []

        results = []

        for account_path in accounts:
            try:
                result = self.generate_for_account(account_path)
                if result:
                    results.append(result)
                    log(f"[{result['account']}] ✓ Post generated + queued.")
            except Exception as e:
                log(f"❌ ERROR in {account_path.name}: {e}")

        return results