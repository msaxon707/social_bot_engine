import shutil
from pathlib import Path
from engine.utils import BASE_DIR, log
from engine.airtable_client import airtable_create


def main():
    template_dir = BASE_DIR / "accounts" / "TEMPLATE_ACCOUNT"
    if not template_dir.exists():
        log("TEMPLATE_ACCOUNT folder not found.")
        return

    name = input("New account folder name (e.g. country_living_1): ").strip()
    niche = input("Niche (e.g. country living): ").strip()
    style_key = input("Style key (e.g. country_living, dogs, hunting, default): ").strip() or "default"
    daily_posts = int(input("Daily posts (e.g. 1, 2, 3): ").strip() or "1")

    new_dir = BASE_DIR / "accounts" / name
    if new_dir.exists():
        log("That account folder already exists.")
        return

    shutil.copytree(template_dir, new_dir)

    # Update settings.json
    settings_path = new_dir / "settings.json"
    import json
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    settings["account_name"] = name
    settings["niche"] = niche
    settings["style_key"] = style_key
    settings["daily_posts"] = daily_posts

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    log(f"Created folder for account: {name}")

    # Create Airtable Accounts row
    airtable_create("Accounts", {
        "Name": name,
        "Niche": niche,
        "Style": style_key,
        "Daily Posts": daily_posts
    })

    log("Created Airtable 'Accounts' record. You can now add Topics linked to this account.")


if __name__ == "__main__":
    main()
