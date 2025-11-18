"""
Scheduler — Runs one bot cycle (Airtable sync + post generation).
Designed to be triggered via cron or Coolify Scheduled Task.
"""

import logging
from dotenv import load_dotenv
from engine.account_manager import AccountManager

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("scheduler")


def run_once():
    """Run a single scheduling pass."""
    log.info("Starting scheduled bot run...")
    try:
        account_manager = AccountManager()
        accounts = account_manager.get_all_accounts()

        for acc_path in accounts:
            account_name = acc_path.name
            log.info(f"Processing account: {account_name}")
            account_manager.generate_for_account(acc_path)

        log.info("Bot run completed successfully ✅")

    except Exception as e:
        log.exception(f"Error during scheduled run: {e}")
    finally:
        log.info("Scheduler finished.")


if __name__ == "__main__":
    run_once()
