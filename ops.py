# Setup logging
import time
from init import setup_logging
from storage import download_file, upload_file


logger = setup_logging()
def sync_files(upload_path: str, download_path: str, remote_path: str) -> None:
    """
    Synchronize files with WebDAV server.
    
    Args:
        upload_path: Local path to file to upload
        download_path: Local path to save downloaded file
        remote_path: Remote path on WebDAV server
    """
    from init import init_webdav_client
    
    client = init_webdav_client()
    
    try:
        # Upload file
        logger.info(f"Uploading {upload_path} to {remote_path}")
        upload_file(client, upload_path, remote_path)
        logger.info("Upload completed successfully")
        
        # Wait for server to process
        logger.info("Waiting 5 seconds for server to process...")
        time.sleep(5)
        
        # Download file
        logger.info(f"Downloading {remote_path} to {download_path}")
        download_file(client, remote_path, download_path)
        logger.info("Download completed successfully")
        
    except Exception as e:
        logger.error(f"Error during file synchronization: {e}", exc_info=True)
        raise