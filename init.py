"""
Initialization module for Server Monitor.

Handles setup of logging, WebDAV client, and paths.
"""

import logging
import os
import urllib3
from webdav3.client import Client

from config import Config

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def setup_logging() -> logging.Logger:
    """
    Configure and return the logger for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def init_webdav_client() -> Client:
    """
    Initialize and return a configured WebDAV client.
    
    Returns:
        Client: Configured WebDAV client
        
    Raises:
        ValueError: If configuration validation fails
    """
    logger = logging.getLogger(__name__)
    
    Config.validate()
    options = Config.get_webdav_options()
    
    client = Client(options)
    client.verify = False
    
    logger.info("WebDAV client initialized successfully")
    return client


def get_paths() -> tuple[str, str, str]:
    """
    Get base directory and file paths.
    
    Returns:
        tuple: (base_dir, upload_path, download_path)
    """
    base_dir = os.getcwd().replace("\\", "/")
    upload_path = f"{base_dir}/upload.json"
    download_path = f"{base_dir}/download.json"
    return base_dir, upload_path, download_path
