from init import setup_logging, get_paths
from ops import sync_files_continuous

# Setup logging
logger = setup_logging()




def main() -> None:

    try:
        # Initialize paths
        base_dir, upload_path, download_path = get_paths()
      
        # Configuration
        remote_path = "json_notifications/CG0128.json"
        logger.info(f"Base directory: {base_dir}")
        logger.info(f"Remote path: {remote_path}")
        
        # Start Checking Server and Syncing Files
        sync_files_continuous(
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
