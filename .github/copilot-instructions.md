# Server Monitor - AI Coding Guidelines

## Project Overview
This is a resident monitoring system that fetches status notifications from a WebDAV server. The core functionality downloads JSON files containing resident status, sensor data, and vital signs, then extracts key information like presence status and timestamps.

## Architecture
- **Entry Point**: `main.py` - Connects to WebDAV, downloads notification JSON, parses resident status
- **Utilities**: `utils.py` - Contains `list_directory()` for WebDAV directory listing
- **Configuration**: `.env` file for WebDAV credentials (USERNAME, PASSWORD, HOSTNAME)
- **Data Flow**: WebDAV client → Download `json_notifications/BL0004.json` → Parse Resident.Status and timestamps

## Key Patterns
- **WebDAV Integration**: Use `webdav3.client.Client` with options dict for hostname/login/password
- **Credential Management**: Load via `python-dotenv` with `load_dotenv(override=True)`
- **Path Handling**: Remote paths use forward slashes, local paths handle Windows backslashes
- **JSON Parsing**: Access nested structures like `json_content["Resident"]["Status"]`
- **SSL Handling**: Disable warnings with `urllib3.disable_warnings()` and set `client.verify = False`

## Developer Workflows
- **Setup**: Run `setup_env.bat` to create virtual environment and install dependencies from `requirements.txt`
- **Configuration**: Edit `.env` with actual WebDAV credentials before running
- **Execution**: `python main.py` downloads and processes the notification file
- **Debugging**: Check console output for connection details and parsed values

## File Structure Conventions
- Remote notifications: `json_notifications/{ID}.json` where ID is like "BL0004"
- Local temp file: `temp.json` in current directory
- JSON structure: Top-level "Resident" object with "Status" and "Timestamp" fields

## Dependencies
Core packages: `webdavclient3`, `python-dotenv`, `urllib3`. Install via `pip install -r requirements.txt` in virtual environment.

## Common Tasks
- **Add New Resident Monitoring**: Copy the download/parse pattern in `main.py`, change the ID in `notif_path`
- **Extend Data Extraction**: Add new fields from the JSON structure (e.g., Sensor.Status, VitalSigns)
- **Error Handling**: Follow the pattern of printing status messages; consider adding try/catch for network operations