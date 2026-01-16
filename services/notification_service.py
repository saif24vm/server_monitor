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
        # Support multiple recipients: EMAIL_RECIPIENTS can be a comma-separated list.
        recipients_raw = os.getenv("EMAIL_RECIPIENTS") 
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))

        if not all([email_sender, email_password, recipients_raw, smtp_server]):
            logger.error("SMTP configuration incomplete")
            raise RuntimeError("SMTP configuration incomplete")

        # Parse recipients into a list, trimming whitespace and ignoring empties
        recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]
        if not recipients:
            logger.error("No valid email recipients configured")
            raise RuntimeError("No valid email recipients configured")

        msg = MIMEMultipart()
        msg["From"] = email_sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = f"Server Monitor Alert - Resident {resident_id}"

        body = f"""
        <html>
          <body>
            <h2>Server Monitor Alert - Resident {resident_id}</h2>
            <p><strong>Resident:</strong> {resident_id}</p>
            <p><strong>Issue:</strong> WebDAV server Upload status and Browser download status do not match. There might be problem in server</p>
            <p><strong>Consecutive Mismatches:</strong> {mismatch_count}</p>
            <p><strong>Timestamp:</strong> {now_utc_iso()}</p>
          </body>
        </html>
        """

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_sender, email_password)
            # send_message accepts an explicit list of recipients
            server.send_message(msg, to_addrs=recipients)

        logger.info(f"Alert email sent for resident {resident_id}")
        return True

    except Exception:
        logger.exception("Failed to send mismatch email")
        return False
