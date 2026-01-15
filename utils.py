import json
import random
from datetime import datetime, timezone
from enums import HUMAN_RANGES, STATE_LIST
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Store latest random state globally
latest_state = None

def random_state():
    global latest_state
    latest_state = random.choice(tuple(STATE_LIST))
    return latest_state


def now_utc_iso():
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def list_directory(client, remote_path="/"):
    """List items in WebDAV directory."""
    print(f"Listing directory: {remote_path}")
    items = client.list(remote_path)

    for item in items:
        print(item)


def manipulate_sensor_json(file_path: str) -> None:
    """
    Mutates upload.json:
    - Random Resident.Status
    - Updated Resident.Timestamp
    - Random human-factor VitalSigns values (only if status is S_PRESENT_BED)
    """

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ---- Resident state ----
    data["Resident"]["Status"] = random_state()
    data["Resident"]["Timestamp"] = now_utc_iso()

    # ---- Vital signs (only update if resident is in bed, else set to 0) ----
    if latest_state == "S_PRESENT_BED":
        data["VitalSigns"] = random_vital_signs()
    else:
        data["VitalSigns"] = {
            "Heart": {
                "Value": 0,
                "Limit": 0
            },
            "Breath": {
                "Value": 0,
                "Limit": 0
            },
            "Temperature": {
                "Value": 0,
                "Limit": 0
            }
        }

    # ---- Root timestamp ----
    data["Timestamp"] = now_utc_iso()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

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


def send_mismatch_email(mismatch_count: int) -> bool:
    try:
        email_sender = os.getenv("EMAIL_SENDER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_recipient = os.getenv("EMAIL_RECIPIENT")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))

        if not all([email_sender, email_password, email_recipient, smtp_server]):
            raise RuntimeError("SMTP configuration incomplete")

        msg = MIMEMultipart()
        msg["From"] = email_sender
        msg["To"] = email_recipient
        msg["Subject"] = "Server Monitor Alert"

        body = f"""
        <html>
          <body>
            <h2>File Mismatch Alert</h2>
            <p>Webdav server upload json files and downloaded file does not match.</p>
            <p>Timestamp: {now_utc_iso()}</p>
          </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_sender, email_password)
            server.send_message(msg)

        return True

    except Exception:
        import traceback
        traceback.print_exc()
        return False


def file_checksum(path: str) -> str:
    """Calculate SHA256 checksum of file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
