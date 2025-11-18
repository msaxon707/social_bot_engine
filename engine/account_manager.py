import random
from pathlib import Path
from urllib.parse import quote_plus
from .utils import load_json, log, BASE_DIR
from .post_generator import generate_post
from .airtable_client import airtable_get, airtable_create, airtable_update


class AccountManager:
    def __init__(self) -> None:
        self.accounts_dir = BASE_DIR / "accounts"
        self.account_name_to_id = self._load_accounts_table()

    # ──────────────────────────────────────────────────────────
    def _load_accounts_table(self) -> dict[str, str]:
        """Load all accounts from Airtable and map names → record IDs."""
        mapping = {}
        for rec in airtable_get("Accounts"):
            name = rec["fields"].get("Name")
            if name:
                mapping[name] = rec["id"]
        log(f"[ACCOUNTS] Loaded {len(mapping)} accounts from Airtable.")
        return mapping

    def get_all_accounts(self) -> list[Path]:
        """Return all account directories except the template."""
        return [
            p for p in self.accounts_dir.iterdir()
            if p.is_dir() and p.name != "TEMPLATE_ACCOUNT"
        ]

    # ──────────────────────────────────────────────────────────
    def _next_topic(self, account_name: str) -> tuple[str, str] | None:
        """Fetch a random 'To Use' topic for a given account."""
        formula = f"AND(Account='{account_name}', Status='To Use')"
        url = (
            "Topics?"
            "fields[]=Topic&fields[]=Account&fields[]=Status&"
            f"filterByFormula={quote_plus(formula)}"
        )

        recs = airtable_get(url)
        if not recs:
            return None

        picked = random.choice(recs)
        return picked["id"], picked["fields"]["Topic"]

    # ──────────────────────────────────────────────────────────
    def generate_for_account(self, account_path: Path) -> None:
        """Generate one post for the given account."""
        account_name = account_path.name
        topic = self._next_topic(account_name)

        if not topic:
            log(f"[{account_name}] No topics available.")
            return

        topic_id, topic_text = topic
        post = generate_post(topic_text, style_key=None)

        if not post:
            log(f"[{account_name}] Post generation failed.")
            return

        # Save to Airtable "Posts"
        log(f"[DEBUG] Final hashtags string: {', '.join([str(h) for h in post.get('hashtags', []) if h])}")
        airtable_create(
            "Posts",
            {
                "Account": [self.account_name_to_id[account_name]],
                "Topic": topic_text,
                "Title": post["title"],
                "Description": post["description"],
                "Hashtags": ", ".join([str(h).strip() for h in post.get("hashtags", []) if h]),
                "Status": "ready",
            },
        )

        # Update the topic as used
        airtable_update("Topics", topic_id, {"Status": "Used"})
        log(f"[{account_name}] Saved post for topic: {topic_text}")
