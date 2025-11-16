"""
Run one scheduling pass, then exit.

Invoke with:
    python -m engine.scheduler
on whatever schedule you prefer (cron, Coolify Scheduled Task, etc.).
"""
import logging
from .account_manager import AccountManager

log = logging.getLogger("scheduler")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


        def run_once() -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    …
    return results          # return empty list instead of None



if __name__ == "__main__":
    run_once()
