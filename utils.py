import json
import random
from datetime import datetime, timezone

HUMAN_RANGES = {
    "Heart": (55, 110),
    "Breath": (10, 25),
    "Temperature": (35.8, 38.5) 
}

STATE_LIST = {
    "S_ABSENT",
    "S_PRESENT_ROOM",
    "S_PRESENT_BED",
    "S_PRESENT_BATHROOM",
}

def random_state():
    return random.choice(tuple(STATE_LIST))


def now_utc_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def list_directory(client, remote_path="/"):
    print(f"Listing directory: {remote_path}")
    items = client.list(remote_path)

    for item in items:
        print(item)


def manipulate_sensor_json(file_path: str) -> None:
    """
    Mutates upload.json:
    - Random Resident.Status
    - Updated Resident.Timestamp
    - Random human-factor VitalSigns values
    """

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ---- Resident state ----
    data["Resident"]["Status"] = random_state()
    data["Resident"]["Timestamp"] = now_utc_iso()

    # ---- Vital signs ----
    data["VitalSigns"] = random_vital_signs()

    # ---- Root timestamp ----
    data["Timestamp"] = now_utc_iso()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def random_vital_signs():
    return {
        "Heart": {
            "Value": random.randint(*HUMAN_RANGES["Heart"]),
            "Limit": 0
        },
        "Breath": {
            "Value": random.randint(*HUMAN_RANGES["Breath"]),
            "Limit": 0
        },
        "Temperature": {
            "Value": round(random.uniform(*HUMAN_RANGES["Temperature"]), 1),
            "Limit": 0
        }
    }
