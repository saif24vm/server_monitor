import signal
import json
import os
from pathlib import Path
from core.initialization import initialize_portal, setup_logging, get_paths, init_webdav_client
from core.monitor import MonitorService

# Setup logging
logger = setup_logging()

# Global flag for graceful shutdown
shutdown_event = False


def signal_handler(signum, frame) -> None:
    """Handle shutdown signals gracefully."""
    global shutdown_event
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event = True


def load_residents_config() -> list:
    """
    Load residents configuration from environment variables.

    The application no longer requires `config/residents.json`.
    Provide the resident id via RESIDENT_ID and interval via RESIDENT_INTERVAL.
    If not provided, falls back to a single default resident.

    Returns:
        list: List of resident configs
    """
    try:
        resident_id = os.getenv("RESIDENT_ID", "CG0128")
        interval = int(os.getenv("RESIDENT_INTERVAL", "10"))
        residents = [{"id": resident_id, "interval": interval}]
        logger.info(f"Configured {len(residents)} resident(s) from environment")
        return residents
    except Exception as e:
        logger.error(f"Failed to load residents config from env: {e}")
        return [{"id": "CG0128", "interval": 10}]


def main() -> None:


    global shutdown_event
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    try:
        # Initialize paths
        base_dir= get_paths()
        logger.info(f"Base directory: {base_dir}")

        # Load residents configuration
        logger.info("Loading residents configuration...")
        residents_config = load_residents_config()
        
        logger.info("Initializing portal authentication...")
        initialize_portal()
        logger.info("Portal data received successfully")
        
        # Initialize WebDAV client
        logger.info("Initializing WebDAV client...")
        init_webdav_client()
        logger.info("WebDAV client initialized")
        
        # Create and start monitor service
        logger.info(f"Starting monitor service for {len(residents_config)} resident(s)")
        monitor_service = MonitorService(
            residents_config=residents_config,
            shutdown_flag=lambda: shutdown_event
        )
        
        monitor_service.start()
        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.critical(f"Application failed: {e}", exc_info=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
