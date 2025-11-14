from .account_manager import AccountManager
from .utils import log, load_json, BASE_DIR
from pathlib import Path


def run_once():
    """
    Simple scheduler: for each account, generate up to 'daily_posts' posts.
    You schedule this script via cron / Coolify (e.g. 1–3 times per day).
    """
    manager = AccountManager()
    accounts = manager.get_all_accounts()

    if not accounts:
        log("No accounts found.")
        return []

    results = []

    for account_path in accounts:
        settings = load_json(account_path / "settings.json")
        daily_posts = settings.get("daily_posts", 1)

        log(f"[{account_path.name}] Target posts this run: {daily_posts}")

        for _ in range(daily_posts):
            result = manager.generate_for_account(account_path)
            if result:
                results.append(result)

    return results
