"""
Initialization module for Server Monitor.

Handles setup of logging, WebDAV client, paths, and portal authentication.
"""

import logging
import os
import json
import urllib3
from webdav3.client import Client
from colorlog import ColoredFormatter
from config import Config
from portal import validate_credentials, browser_login, create_authenticated_session, call_authenticated_api

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    global client
    logger = logging.getLogger(__name__)
    
    Config.validate()
    options = Config.get_webdav_options()
    
    client = Client(options)
    client.verify = False
    
    logger.info("WebDAV client initialized successfully")
    return client

def get_saved_client():

    """  Get the saved WebDAV client.
    
    """
    return client


def initialize_portal() -> dict:
    """Initialize portal: validate credentials, login, and fetch sensor data.
    
    Returns:
        dict: Sensor data from the authenticated API call
    """
    global saved_session
    logger = logging.getLogger(__name__)
    
    logger.info("Step 1: Validating backend credentials...")
    validate_credentials()
    
    logger.info("Step 2: Performing browser-based login...")
    cookies = browser_login()
    
    logger.info("Step 3: Creating authenticated session...")
    saved_session = create_authenticated_session(cookies)
    

def get_saved_session():
    """Get the saved authenticated session.
    
    Returns:
        requests.Session: The authenticated session, or None if not initialized
    """
    return saved_session





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
