"""Core monitoring engine for Server Monitor."""

import os
import time
import logging
from core.initialization import get_saved_client, get_saved_session
from services.resident_monitor import ResidentMonitor
from services.notification_service import send_mismatch_email


logger = logging.getLogger(__name__)


class MonitorService:
    """Service for continuous monitoring of residents."""
    
    def __init__(self, residents_config: list, shutdown_flag=None):
        """
        Initialize monitor service.
        
        Args:
            residents_config: List of resident configs with id, interval, etc.
            shutdown_flag: Callable that returns True when shutdown is requested
        """
        self.residents_config = residents_config
        self.shutdown_flag = shutdown_flag
        self.monitors = {}
        self._initialize_monitors()
    
    def _initialize_monitors(self):
        """Initialize monitors for each resident."""
        for config in self.residents_config:
            resident_id = config.get("id")
            interval = config.get("interval", 60)
            monitor = ResidentMonitor(
                resident_id=resident_id,
                interval_sec=interval
            )
            self.monitors[resident_id] = monitor
            logger.info(f"Initialized monitor for resident {resident_id}")
    
    def start(self) -> None:
        """
        Start continuous monitoring of all residents.
        Runs until shutdown_flag is set.
        """
        logger.info(f"Starting monitor service for {len(self.monitors)} residents")
        
        while not (self.shutdown_flag and self.shutdown_flag()):
            try:
                # Get client and session for each cycle
                client = get_saved_client()
                session = get_saved_session()
                
                for resident_id, monitor in self.monitors.items():
                    success = monitor.sync_once(client=client, session=session)
                    if not success:
                        logger.warning(f"Sync failed for resident {resident_id}")
                
                # Sleep based on minimum interval
                min_interval = min(
                    (config.get("interval", 60) for config in self.residents_config),
                    default=60
                )
                logger.debug(f"Sleeping for {min_interval} seconds")
                time.sleep(min_interval)
                
            except Exception:
                logger.exception("Monitor cycle failed")
                time.sleep(5)
        
        logger.info("Graceful shutdown of monitor service complete")
