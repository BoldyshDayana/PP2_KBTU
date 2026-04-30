# Save/load leaderboard and settings to JSON files

import json, os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal",
    "username": "",
}

# Settings 

def load_settings() -> dict:
    """Load settings.json; missing keys fall back to DEFAULT_SETTINGS."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(s: dict) -> None:
    """Write settings dict to settings.json."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f, indent=2)
    except IOError as e:
        print(f"[persistence] settings save failed: {e}")

# Leaderboard 

def load_leaderboard() -> list:
    """Load leaderboard.json; returns [] on error or missing file."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE) as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def save_leaderboard(entries: list) -> None:
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except IOError as e:
        print(f"[persistence] leaderboard save failed: {e}")

def add_leaderboard_entry(name: str, score: int, distance: int, coins: int) -> list:
    """Add entry, keep top-10 by score, save and return updated list"""
    entries = load_leaderboard()
    entries.append({"name": name, "score": score,
                    "distance": distance, "coins": coins})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    save_leaderboard(entries)
    return entries