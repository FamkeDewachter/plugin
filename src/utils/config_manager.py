# utils/config_manager.py
import json
import os


def get_stored_drive_id():
    """Retrieve the stored Drive ID from a config file."""
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
        return config.get("drive_id")
    return None


def store_drive_id(drive_id):
    """Store the selected Drive ID in a config file."""
    with open("config.json", "w") as f:
        json.dump({"drive_id": drive_id}, f)
