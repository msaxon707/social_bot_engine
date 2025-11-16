import random
from pathlib import Path
from .utils import load_json, log, BASE_DIR
from .post_generator import generate_post
from .airtable_client import airtable_get, airtable_create, airtable_update

class AccountManager:
    def __init__(self) -> None:
        self.accounts_dir = BASE_DIR / "accounts"
        self.account_name_to_id = self._load_accounts_table()

    # ──────────────────────────────────────────────────────────
    def _load_accounts_table(self) -> dict[str, str]:
        mapping = {}
        for rec in airtable_get("Accounts"):
            name = rec["fields"].get("Name")
            if name:
                mapping[name] = rec["id"]
        log(f"[ACCOUNTS] Loaded {len(mapping)} accounts from Airtable.")
        return mapping

    def get_all_accounts(self) -> list[Path]:
        return [
            p for p in self.accounts_dir.iterdir()
            if p.is_dir() and p.name != "TEMPLATE_ACCOUNT"
        ]

    # ──────────────────────────────────────────────────────────
    def _next_topic(self, account_name: str) -> tuple[str, str] | None:
        formula = f"AND(Account='{account_name}',Status='To Use')"
        recs = airtable_get("Topics?fields[]=Topic&fields[]=Account&fields[]=Status&filterByFormula={formula}")
        if not recs:
            return None
        picked = random.choice(recs)
        return picked["id"], picked["fields"]["Topic"]

    # ──────────────────────────────────────────────────────────
    def generate_for_account(self, account_path: Path) -> None:
        account_name = account_path.name
        topic = self._next_topic(account_name)
        if not topic:
            log(f"[{account_name}] No topics.")
            return
        topic_id, topic_text = topic

        post = generate_post(topic_text, style_key=None)
        if not post:
            log(f"[{account_name}] Post generation failed.")
            return

        # save to Airtable Posts
        airtable_create(
            "Posts",
            {
                "Account": [self.account_name_to_id[account_name]],
                "Topic": topic_text,
                "Title": post["title"],
                "Description": post["description"],
                "Hashtags": ", ".join(post["hashtags"]),
                "Status": "ready",
            },
        )
        airtable_update("Topics", topic_id, {"Status": "Used"})
        log(f"[{account_name}] Saved post for topic: {topic_text}")
