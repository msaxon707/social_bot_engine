import json
from pathlib import Path
from .utils import load_json, load_lines, log, BASE_DIR
from .post_generator import generate_post

class AccountManager:
    def __init__(self):
        self.accounts_dir = BASE_DIR / "accounts"

    def get_all_accounts(self):
        """Return a list of account directories, excluding TEMPLATE."""
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

        # choose a random topic
        import random
        topic = random.choice(topics)

        style = settings.get("style", None)

        log(f"[{account_name}] Generating post for topic: {topic}")

        generated = generate_post(topic, style)

        return {
            "account": account_name,
            "topic": topic,
            "post": generated
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
                    log(f"[{result['account']}] Post generated successfully.")
            except Exception as e:
                log(f"ERROR in {account_path.name}: {e}")

        return results
