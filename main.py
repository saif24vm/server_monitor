from init import initialize_portal, setup_logging, get_paths, init_webdav_client
from ops import start_server_check

# Setup logging
logger = setup_logging()




def main() -> None:
    """Main entry point for server monitor application."""
    try:
        # Initialize paths
        base_dir, upload_path, download_path = get_paths()
      
        # Configuration
        remote_path = "json_notifications/CG0128.json"
        logger.info(f"Base directory: {base_dir}")
        logger.info(f"Remote path: {remote_path}")

        logger.info("Initializing portal authentication...")
        initialize_portal()
        logger.info("Portal data received successfully")
        
        # Initialize WebDAV client
        logger.info("Initializing WebDAV client...")
        init_webdav_client()
        logger.info("WebDAV client initialized")
        
        # Start Checking Server and Syncing Files
        start_server_check(
            upload_path="upload.json",
            download_path="download.json",
            remote_path="json_notifications/CG0128.json",
            interval_sec=10
        )

        
        logger.info("Application completed successfully")
        
    except Exception as e:
        logger.critical(f"Application failed: {e}", exc_info=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
