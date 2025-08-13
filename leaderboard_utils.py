import os
import json
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"

def save_score(username, score, total):
    entry = {
        "username": username,
        "score": score,
        "total": total,
        "timestamp": datetime.now().isoformat(timespec='minutes')
    }

    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(entry)

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []  # File is empty
            return json.loads(content)
    except json.JSONDecodeError:
        return []  # File is malformed