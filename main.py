from webdav3.client import Client
import urllib3
import os
import time
from config import Config
from storage import upload_file, download_file
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---- Load and validate configuration ----
Config.validate()
options = Config.get_webdav_options()

client = Client(options)
client.verify = False

# ---- Paths ----
base_dir = os.getcwd().replace("\\", "/")

temp_upload_file_path = f"{base_dir}/upload.json"
temp_download_file_path = f"{base_dir}/download.json"

remote_path = "json_notifications/CG0128.json"


# ---- Step 1: Upload ----
upload_file(client, temp_upload_file_path, remote_path)
print("Upload completed")

# ---- Step 2: Wait 5 seconds ----
time.sleep(5)

# ---- Step 3: Download ----
download_file(client, remote_path, temp_download_file_path)
print("Download completed")
