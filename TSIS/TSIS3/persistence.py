import json
import os

SETTINGS_FILE = 'settings.json'
LEADERBOARD_FILE = 'leaderboard.json'

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "RED",
    "difficulty": "Medium"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_score(name, score, distance, coins):
    scores = load_leaderboard()
    scores.append({"name": name, "score": score, "distance": distance, "coins": coins})
    scores.sort(key=lambda x: (x['score'], x.get('distance', 0)), reverse=True)
    scores = scores[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(scores, f, indent=4)
