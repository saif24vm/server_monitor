"""
Initialization module for Server Monitor.

Handles setup of logging, WebDAV client, paths, and portal authentication.
"""

import logging
import os
import urllib3
from webdav3.client import Client
from colorlog import ColoredFormatter
from config.config import Config
from core.portal import validate_credentials, browser_login, create_authenticated_session

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global instances
_client = None
_saved_session = None


def setup_logging() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
        }
    )

    handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(handler)

    return logger


def init_webdav_client() -> Client:
    """
    Initialize and return a configured WebDAV client.
    
    Returns:
        Client: Configured WebDAV client
        
    Raises:
        ValueError: If configuration validation fails
    """
    global _client
    logger = logging.getLogger(__name__)
    
    Config.validate()
    options = Config.get_webdav_options()
    
    _client = Client(options)
    _client.verify = False
    
    logger.info("WebDAV client initialized successfully")
    return _client


def get_saved_client() -> Client:
    """Get the saved WebDAV client.
    
    Returns:
        Client: The configured WebDAV client
    """
    global _client
    if _client is None:
        raise RuntimeError("WebDAV client not initialized. Call init_webdav_client() first.")
    return _client


def initialize_portal() -> None:
    """Initialize portal: validate credentials, login, and fetch sensor data."""
    global _saved_session
    logger = logging.getLogger(__name__)
    
    logger.info("Step 1: Validating backend credentials...")
    validate_credentials()
    
    logger.info("Step 2: Performing browser-based login...")
    cookies = browser_login()
    
    logger.info("Step 3: Creating authenticated session...")
    _saved_session = create_authenticated_session(cookies)


def get_saved_session():
    """Get the saved authenticated session.
    
    Returns:
        requests.Session: The authenticated session, or None if not initialized
    """
    global _saved_session
    return _saved_session


def get_paths() -> tuple[str, str, str]:
    """
    Get base directory and file paths.
    
    Returns:
        tuple: (base_dir, upload_path, download_path)
    """
    base_dir = os.getcwd().replace("\\", "/")
    upload_path = f"{base_dir}/data/upload.json"
    download_path = f"{base_dir}/data/download.json"
    return base_dir, upload_path, download_path
