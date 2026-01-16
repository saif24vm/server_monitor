"""Configuration module for server_monitor."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# VMedD Portal Configuration
BASE_URL = "https://vmedd-portal.de"
LOGIN_API_URL = f"{BASE_URL}/ems/vmedd-monitor/fo/portal/loginWidget.json"
SENSOR_INFO_URL = f"{BASE_URL}/ems/vmedd-monitor/fo/portal/vmeddNotifications.json"
START_URL = f"{BASE_URL}/ems/vmedd-monitor/fo/portal/start"
LOGGED_IN_URL = "/ems/vmedd-monitor/fo/portal/home"


class Config:
    """Configuration class for WebDAV credentials."""
    
    WEBDAV_USERNAME = os.getenv("USERNAME")
    WEBDAV_PASSWORD = os.getenv("PASSWORD")
    WEBDAV_HOSTNAME = os.getenv("HOSTNAME")
    
    @classmethod
    def get_webdav_options(cls):
        """Return WebDAV client options dictionary."""
        if not all([cls.WEBDAV_USERNAME, cls.WEBDAV_PASSWORD, cls.WEBDAV_HOSTNAME]):
            raise ValueError("Missing WebDAV credentials in .env file")
        
        return {
            'webdav_hostname': cls.WEBDAV_HOSTNAME,
            'webdav_login': cls.WEBDAV_USERNAME,
            'webdav_password': cls.WEBDAV_PASSWORD,
        }
    
    @classmethod
    def validate(cls):
        """Validate that all required credentials are present."""
        missing = []
        if not cls.WEBDAV_USERNAME:
            missing.append("USERNAME")
        if not cls.WEBDAV_PASSWORD:
            missing.append("PASSWORD")
        if not cls.WEBDAV_HOSTNAME:
            missing.append("HOSTNAME")
        
        if missing:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")
        
        print(f"[OK] Configuration loaded: {cls.WEBDAV_HOSTNAME}")
