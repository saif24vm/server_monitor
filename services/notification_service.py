"""Notification service for alerts and emails."""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.time_utils import now_utc_iso


logger = logging.getLogger(__name__)


def send_mismatch_email(resident_id: str, mismatch_count: int) -> bool:
    """
    Send email alert for resident status mismatch.
    
    Args:
        resident_id: Resident identifier
        mismatch_count: Number of consecutive mismatches
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        email_sender = os.getenv("EMAIL_SENDER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_recipient = os.getenv("EMAIL_RECIPIENT")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))

        if not all([email_sender, email_password, email_recipient, smtp_server]):
            logger.error("SMTP configuration incomplete")
            raise RuntimeError("SMTP configuration incomplete")

        msg = MIMEMultipart()
        msg["From"] = email_sender
        msg["To"] = email_recipient
        msg["Subject"] = f"Server Monitor Alert - Resident {resident_id}"

        body = f"""
        <html>
          <body>
            <h2>Server Monitor Alert - Resident {resident_id}</h2>
            <p><strong>Resident:</strong> {resident_id}</p>
            <p><strong>Issue:</strong> WebDAV server upload and downloaded files do not match.</p>
            <p><strong>Consecutive Mismatches:</strong> {mismatch_count}</p>
            <p><strong>Timestamp:</strong> {now_utc_iso()}</p>
          </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_sender, email_password)
            server.send_message(msg)

        logger.info(f"Alert email sent for resident {resident_id}")
        return True

    except Exception:
        logger.exception("Failed to send mismatch email")
        return False
