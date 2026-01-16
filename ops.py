# Setup logging
import os
import time
import json
from init import get_saved_client, setup_logging, get_saved_session
from storage import download_file, upload_file
from utils import extract_resident_status, get_latest_state, send_mismatch_email
from portal import call_authenticated_api


logger = setup_logging()

# Track consecutive mismatches
mismatch_count = 0

def get_resident_status_from_file(file_path: str) -> str:
    """Extract resident status from downloaded JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("Resident", {}).get("Status", "UNKNOWN")
    except Exception as e:
        logger.error(f"Error reading resident status from file: {e}")
        return "ERROR"

def start_server_check(
    upload_path: str,
    download_path: str,
    remote_path: str,
    interval_sec: int = 60,
    shutdown_flag=None
) -> None:
    """
    Continuously synchronize files with WebDAV every `interval_sec` seconds.
    Compares resident status from authenticated API with downloaded file.
    Sends email alert if statuses mismatch 6 times consecutively.
    
    Args:
        shutdown_flag: Callable that returns True when shutdown is requested
    """
    global mismatch_count
    logger.info("Starting continuous file synchronization (interval=%ss)", interval_sec)
    client = get_saved_client()

    while not (shutdown_flag and shutdown_flag()):
        try:
            
            logger.info("Uploading %s to %s", upload_path, remote_path)
            upload_file(client, upload_path, remote_path)
            logger.info("Waiting 5 seconds for server processing")

            if not os.path.exists(download_path):
                logger.warning("Downloaded file missing after sync")
                mismatch_count += 1
            else:
                # Get resident status from authenticated API
                logger.debug("Fetching resident status from authenticated API...")
                session = get_saved_session()
                
                if session is None:
                    logger.error("Session not initialized. Please call initialize_portal() first.")
                    mismatch_count += 1
                else:
                    api_data = call_authenticated_api(session)
                    logger.debug(api_data)
                    api_status = extract_resident_status(api_data, "CG0128")
                    
                    # Get resident status from downloaded file
                    #file_status = get_resident_status_from_file(download_path)
                    latest_state = get_latest_state()
                    logger.info(f"Portal Resident Status: {api_status}")
                    logger.info(f"Latest State Status: {latest_state}")
                    if api_status != latest_state:
                        mismatch_count += 1
                        logger.warning(
                            f"Resident status mismatch detected ({mismatch_count}/6): API status={api_status},"
                        )
                        # Send email alert when mismatch reaches 6 times
                        if mismatch_count == 6:
                            logger.critical("Resident status mismatch reached 6 times! Sending email alert...")
                            send_mismatch_email(mismatch_count)
                            mismatch_count = 0  # Reset counter after sending email
                    else:
                        logger.info("Resident status verified: API and file statuses match")
                        mismatch_count = 0  # Reset counter on successful match

        except Exception:
            logger.exception("Synchronization cycle failed")

        logger.info("Sleeping for %s seconds", interval_sec)
        time.sleep(interval_sec)

    logger.info("Graceful shutdown complete")
def sync_files_once(upload_path: str, download_path: str, remote_path: str) -> None:
    """
    Perform a single upload → wait → download cycle.
    """
    
    client = get_saved_client()

    logger.info("Uploading %s to %s", upload_path, remote_path)
    upload_file(client, upload_path, remote_path)

    logger.info("Waiting 5 seconds for server processing")
    time.sleep(5)

    logger.info("Downloading %s to %s", remote_path, download_path)
    download_file(client, remote_path, download_path)

    logger.info("Single synchronization completed")
