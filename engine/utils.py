import json
from pathlib import Path
from datetime import datetime

# Base directory of the repo (one level up from /engine)
BASE_DIR = Path(__file__).resolve().parent.parent

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_lines(path):
    """Load non-empty, stripped lines from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def ensure_dir(path: Path):
    """Make sure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)

def log(message: str):
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}")
