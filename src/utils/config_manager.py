# utils/config_manager.py
import json
import os


def get_stored_drive_data():
    """Retrieve the stored drive data (selected_drive_id and all_drives) from the config file."""
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
        return config.get("selected_drive_id"), config.get("all_drives", [])
    return None, []


def store_drive_data(selected_drive_id, all_drives):
    """Store the selected Drive ID and all available drives in a config file."""
    config = {"selected_drive_id": selected_drive_id, "all_drives": all_drives}
    with open("config.json", "w") as f:
        json.dump(config, f)
