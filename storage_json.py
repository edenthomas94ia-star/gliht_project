import json
from pathlib import Path
from datetime import datetime

DATA_PATH = Path("data/flights.json")


def load_flights():
    if not DATA_PATH.exists():
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_flights(new_offers):
    DATA_PATH.parent.mkdir(exist_ok=True)

    old_data = load_flights()

    timestamp = datetime.utcnow().isoformat()

    for offer in new_offers:
        offer["collected_at"] = timestamp

    all_data = old_data + new_offers

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)