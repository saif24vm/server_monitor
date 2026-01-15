# Setup logging
import os
import time
from init import setup_logging
from storage import download_file, upload_file
from utils import file_checksum, send_mismatch_email


logger = setup_logging()

# Track consecutive mismatches
mismatch_count = 0

def sync_files_continuous(
    upload_path: str,
    download_path: str,
    remote_path: str,
    interval_sec: int = 60
) -> None:
    """
    Continuously synchronize files with WebDAV every `interval_sec` seconds.
    Sends email alert if files mismatch 6 times consecutively.
    """
    global mismatch_count
    logger.info("Starting continuous file synchronization (interval=%ss)", interval_sec)

    while True:
        try:
            sync_files_once(upload_path, download_path, remote_path)

            if not os.path.exists(upload_path) or not os.path.exists(download_path):
                logger.warning("One or both files missing after sync")
                mismatch_count += 1
            else:
                upload_hash = file_checksum(upload_path)
                download_hash = file_checksum(download_path)

                if upload_hash != download_hash:
                    mismatch_count += 1
                    logger.warning(
                        f"File mismatch detected ({mismatch_count}/6): uploaded and downloaded files differ"
                    )
                    # Send email alert when mismatch reaches 6 times
                    if mismatch_count == 6:
                        logger.critical("File mismatch reached 6 times! Sending email alert...")
                        send_mismatch_email(mismatch_count)
                        mismatch_count = 0  # Reset counter after sending email
                else:
                    logger.info("File integrity verified: files match")
                    mismatch_count = 0  # Reset counter on successful match

        except Exception:
            logger.exception("Synchronization cycle failed")

        logger.info("Sleeping for %s seconds", interval_sec)
        time.sleep(interval_sec)

        
def sync_files_once(upload_path: str, download_path: str, remote_path: str) -> None:
    """
    Perform a single upload → wait → download cycle.
    """
    from init import init_webdav_client

    client = init_webdav_client()

    logger.info("Uploading %s to %s", upload_path, remote_path)
    upload_file(client, upload_path, remote_path)

    logger.info("Waiting 5 seconds for server processing")
    time.sleep(5)

    logger.info("Downloading %s to %s", remote_path, download_path)
    download_file(client, remote_path, download_path)

    logger.info("Single synchronization completed")
