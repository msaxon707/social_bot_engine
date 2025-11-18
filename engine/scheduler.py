"""
Scheduler — Runs one bot cycle (Airtable sync + post generation).
Designed to be triggered via cron or Coolify Scheduled Task.
"""

import logging
from engine.account_manager import AccountManager
from engine.post_generator import generate_post
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scheduler")

def run_once():
    """Run a single scheduling pass."""
    log.info("Starting scheduled bot run...")
    try:
        account_manager = AccountManager()
        accounts = account_manager.get_all_accounts()
        for acc in accounts:
            log.info(f"Processing account: {acc['name']}")
            generate_posts(acc)
        log.info("Bot run completed successfully ✅")
    except Exception as e:
        log.exception(f"Error during scheduled run: {e}")
    finally:
        log.info("Scheduler finished.")

if __name__ == "__main__":
    run_once()
