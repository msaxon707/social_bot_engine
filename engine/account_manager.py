import random
from pathlib import Path
from .utils import load_json, load_lines, log, BASE_DIR
from .post_generator import generate_post
from .content_queue import save_post_to_queue

class AccountManager:
    def __init__(self):
        self.accounts_dir = BASE_DIR / "accounts"

    def get_all_accounts(self):
        """Return a list of account directories, excluding TEMPLATE_ACCOUNT."""
        accounts = []
        for folder in self.accounts_dir.iterdir():
            if folder.is_dir() and folder.name != "TEMPLATE_ACCOUNT":
                accounts.append(folder)
        return accounts

    def load_account_settings(self, account_path: Path):
        settings = load_json(account_path / "settings.json")
        topics = load_lines(account_path / "topics.txt")
        affiliates = load_json(account_path / "affiliates.json")

        return {
            "settings": settings,
            "topics": topics,
            "affiliates": affiliates
        }

    def generate_for_account(self, account_path: Path):
        account_name = account_path.name
        data = self.load_account_settings(account_path)

        settings = data["settings"]
        topics = data["topics"]

        if not topics:
            log(f"[{account_name}] No topics found.")
            return None

        topic = random.choice(topics)
        style = settings.get("style")

        log(f"[{account_name}] Generating post for topic: {topic}")

        post = generate_post(topic, style)

        # Save to local content queue
        queue_path = save_post_to_queue(account_name, topic, post)

        return {
            "account": account_name,
            "topic": topic,
            "post": post,
            "queue_path": str(queue_path)
        }

    def run_all(self):
        accounts = self.get_all_accounts()

        if not accounts:
            log("No accounts found.")
            return []

        results = []

        for account_path in accounts:
            try:
                result = self.generate_for_account(account_path)
                if result:
                    results.append(result)
                    log(f"[{result['account']}] Post generated and queued.")
            except Exception as e:
                log(f"ERROR in {account_path.name}: {e}")

        return results
