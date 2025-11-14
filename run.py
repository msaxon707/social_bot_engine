from engine.account_manager import AccountManager
from engine.utils import log

def main():
    log("Starting multi-account engine...")

    manager = AccountManager()
    results = manager.run_all()

    log("----- SUMMARY FOR THIS RUN -----")
    for r in results:
        log(f"[{r['account']}] Topic: {r['topic']}")
        log(f"Title: {r['post']['title']}")
        log("---")

    log("Engine finished.")

if __name__ == "__main__":
    main()
