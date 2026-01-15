from dotenv import load_dotenv
from webdav3.client import Client
import urllib3
import json
import os

from storage import download_file, upload_file
from utils import list_directory
 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOSTNAME = os.getenv("HOSTNAME")
options = {
  'webdav_hostname': HOSTNAME,
  'webdav_login':    USERNAME,
  'webdav_password': PASSWORD,
}
print(options)
client = Client(options)
client.verify = False
 
currentDirectory = os.getcwd()
cur_dir_mani = currentDirectory.replace("\\", "/")
print(cur_dir_mani)
temp_download_file_path = cur_dir_mani + "/download.json"
sensor_path = "json_notifications/" + "BL0004" + ".json"
#list_directory(client,"json_notifications/")



temp_upload_file_path = cur_dir_mani + "/upload.json"
download_file(client,sensor_path, temp_download_file_path )
#upload_file(client, temp_upload_file_path, sensor_path)