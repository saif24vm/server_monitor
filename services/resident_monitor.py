"""Individual resident monitoring service."""

import os
import time
import logging
from core.storage import download_file, upload_file
from utils.json_utils import extract_resident_status, get_resident_status_from_file
from services.state_manager import StateManager
from core.portal import call_authenticated_api


logger = logging.getLogger(__name__)


class ResidentMonitor:
    """Monitors a single resident's status."""
    
    def __init__(self, resident_id: str, interval_sec: int = 60):
        """
        Initialize resident monitor.
        
        Args:
            resident_id: Unique resident identifier (e.g., "CG0128")
            interval_sec: Sync interval in seconds
        """
        self.resident_id = resident_id
        self.interval_sec = interval_sec
        self.mismatch_count = 0
        self.state_manager = StateManager()
        
        # Paths
        self.upload_path = f"data/upload.json"
        self.download_path = f"data/download.json"
        self.remote_path = f"json_notifications/{resident_id}.json"
    
    def sync_once(self, client=None, session=None) -> bool:
        """
        Perform single sync cycle for this resident.
        
        Args:
            client: WebDAV client instance
            session: Authenticated session for API calls
        
        Returns:
            bool: True if sync successful, False otherwise
        """
        try:
            if client is None or session is None:
                logger.error(f"Missing client or session for resident {self.resident_id}")
                self.mismatch_count += 1
                return False
            
            logger.info(f"[{self.resident_id}] Uploading to {self.remote_path}")
            upload_file(client, self.upload_path, self.remote_path)
            
            # Update state manager with new generated status
            new_status = get_resident_status_from_file(self.upload_path)
            self.state_manager.save_state(self.resident_id, new_status)
            
            logger.debug(f"[{self.resident_id}] Waiting 5 seconds for server processing")
            time.sleep(5)
            
            if not os.path.exists(self.download_path):
                logger.warning(f"[{self.resident_id}] Downloaded file missing after sync")
                self.mismatch_count += 1
                return False
            
            # Get statuses from API and local file
            logger.debug(f"[{self.resident_id}] Fetching resident status from API")
            api_data = call_authenticated_api(session)
            api_status = extract_resident_status(api_data, self.resident_id)
            
            # Get latest state from state manager
            latest_state = self.state_manager.get_latest_state(self.resident_id)
            
            logger.info(f"[{self.resident_id}] Portal Status: {api_status}")
            logger.info(f"[{self.resident_id}] Latest State: {latest_state}")
            
            # Initialize state on first run if not found
            if latest_state is None:
                logger.info(f"[{self.resident_id}] Initializing state with API status: {api_status}")
                self.state_manager.save_state(self.resident_id, api_status)
                return True
            
            if api_status != latest_state:
                self.mismatch_count += 1
                logger.warning(
                    f"[{self.resident_id}] Status mismatch ({self.mismatch_count}/6): "
                    f"API={api_status}, State={latest_state}"
                )
                
                # Send alert after 6 consecutive mismatches
                if self.mismatch_count == 6:
                    logger.critical(
                        f"[{self.resident_id}] Mismatch reached 6 times! Sending alert..."
                    )
                    from services.notification_service import send_mismatch_email
                    send_mismatch_email(self.resident_id, self.mismatch_count)
                    self.mismatch_count = 0
            else:
                logger.info(f"[{self.resident_id}] Status verified - match confirmed")
                self.mismatch_count = 0
                self.state_manager.save_state(self.resident_id, api_status)
            
            return True
            
        except Exception:
            logger.exception(f"[{self.resident_id}] Sync failed")
            self.mismatch_count += 1
            return False
