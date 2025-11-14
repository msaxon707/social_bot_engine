from engine.scheduler import run_once
from engine.utils import log


def main():
    log("Starting scheduled run...")
    results = run_once()

    log("----- SUMMARY FOR THIS RUN -----")
    for r in results:
        log(f"[{r['account']}] Topic: {r['topic']}")
        log(f"  Title: {r['post']['title']}")
        log(f"  JSON:  {r['queue_path']}")
        if r.get("image_path"):
            log(f"  Image: {r['image_path']}")
        if r.get("video_path"):
            log(f"  Video: {r['video_path']}")
        log("----")

    log("Run complete.")


if __name__ == "__main__":
    main()
