"""JSON utilities for sensor data manipulation."""

import json
import random
import hashlib
import logging
from models.enums import HUMAN_RANGES, STATE_LIST
from utils.time_utils import now_utc_iso


logger = logging.getLogger(__name__)

# Store latest random state globally
latest_state = None


def random_state():
    """Return random state from STATE_LIST."""
    global latest_state
    latest_state = random.choice(tuple(STATE_LIST))
    return latest_state


def manipulate_sensor_json(file_path: str) -> None:
    """
    Mutates upload.json:
    - Random Resident.Status
    - Updated Resident.Timestamp
    - Random human-factor VitalSigns values (only if status is S_PRESENT_BED)
    """
    global latest_state
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ---- Resident state ----
        data["Resident"]["Status"] = random_state()
        data["Resident"]["Timestamp"] = now_utc_iso()

        # ---- Vital signs ----
        if latest_state == "S_PRESENT_BED":
            data["VitalSigns"] = random_vital_signs()
        else:
            data["VitalSigns"] = {
                "Heart": {"Value": 0, "Limit": 0},
                "Breath": {"Value": 0, "Limit": 0},
                "Temperature": {"Value": 0, "Limit": 0}
            }

        # ---- Root timestamp ----
        data["Timestamp"] = now_utc_iso()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception:
        logger.exception(f"Failed to manipulate JSON file {file_path}")
        raise


def random_vital_signs():
    """Generate random vital signs within human ranges."""
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


def file_checksum(path: str) -> str:
    """Calculate SHA256 checksum of file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_resident_status(api_response: dict, sensor_id: str) -> str:
    """
    Extract resident status from API response.
    
    Args:
        api_response: API response dictionary
        sensor_id: Sensor/resident identifier
    
    Returns:
        str: Resident status
    
    Raises:
        KeyError: If sensor not found
        ValueError: If status data missing or invalid
    """
    # Check sensor exists
    if sensor_id not in api_response:
        raise KeyError(f"Sensor '{sensor_id}' not found in response")

    sensor_entry = api_response[sensor_id]

    # Check notification exists
    notification_raw = sensor_entry.get("notification")
    if not notification_raw:
        raise ValueError(f"Sensor '{sensor_id}' has no notification data")

    # Parse inner JSON
    try:
        notification = json.loads(notification_raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid notification JSON for sensor '{sensor_id}'"
        ) from e

    # Extract resident status
    resident = notification.get("Resident")
    if not resident or "Status" not in resident:
        raise ValueError(
            f"Resident status missing for sensor '{sensor_id}'"
        )

    return resident["Status"]

def get_resident_status_from_file(file_path: str) -> str:
    """Extract resident status from local JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("Resident", {}).get("Status", "UNKNOWN")
    except Exception as e:
        logger.error(f"Error reading resident status from file: {e}")
        return "ERROR"