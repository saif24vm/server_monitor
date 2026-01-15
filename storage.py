import json

from utils import manipulate_sensor_json


def download_file(client, notif_path, temp_local_file_path):
    """Download JSON file from WebDAV and extract resident status."""
    client.download_sync(remote_path = notif_path, local_path = temp_local_file_path)
    f = open(temp_local_file_path,encoding='utf8')
    json_content_temp = json.load(f)
    f.close()
    status = json_content_temp["Resident"]["Status"]
    timestamp_status = json_content_temp["Resident"]["Timestamp"]
    timestamp_notif = json_content_temp["Timestamp"]
    return status, timestamp_status, timestamp_notif


def upload_file(client, local_path, remote_path):
    """
    Upload a local file to WebDAV.
    """
    manipulate_sensor_json(local_path)
    client.upload_sync(
        remote_path=remote_path,
        local_path=local_path
    )
