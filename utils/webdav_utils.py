"""WebDAV utility functions."""

import logging


logger = logging.getLogger(__name__)


def list_directory(client, remote_path="/"):
    """List items in WebDAV directory.
    
    Args:
        client: WebDAV client instance
        remote_path: Remote directory path to list
    """
    logger.info(f"Listing directory: {remote_path}")
    try:
        items = client.list(remote_path)
        for item in items:
            logger.info(item)
    except Exception:
        logger.exception(f"Failed to list directory: {remote_path}")
