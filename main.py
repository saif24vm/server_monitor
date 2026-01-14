from dotenv import load_dotenv
from webdav3.client import Client
import urllib3
import json
import os

from utils import list_directory
 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOSTNAME = os.getenv("HOSTNAME")
print(PASSWORD)
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
temp_local_file_path = cur_dir_mani + "/temp.json"
notif_path = "json_notifications/" + "BL0004" + ".json"

list_directory(client,"json_notifications/")

# print('##### start download notif')
 
def get_notif(client,notif_path, temp_local_file_path ):
    client.download_sync(remote_path = notif_path, local_path = temp_local_file_path)
    print('##### download notif sucessful')
    f = open(temp_local_file_path,encoding='utf8')
    json_content_temp = json.load(f)
    f.close()
    status = json_content_temp["Resident"]["Status"]
    timestamp_status = json_content_temp["Resident"]["Timestamp"]
    timestamp_notif = json_content_temp["Timestamp"]
    return status, timestamp_status, timestamp_notif
 
 
status, timestamp_status, timestamp_notif = get_notif(client,notif_path, temp_local_file_path)
#print('new status', status, timestamp_status, timestamp_notif)