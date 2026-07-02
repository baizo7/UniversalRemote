import json
import os

SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # Migrate old settings format to new format
                if "devices" not in data:
                    old_ip = data.get("TV_IP", "10.33.225.16")
                    return {"devices": {"Device 1": old_ip}, "active": "Device 1"}
                return data
        except Exception:
            pass
    return {"devices": DEFAULT_DEVICES, "active": "Sony TV"}

def save_settings(devices, active):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"devices": devices, "active": active}, f)
    global TV_IP, DEVICES, ACTIVE_DEVICE
    DEVICES = devices
    ACTIVE_DEVICE = active
    TV_IP = devices.get(active, "127.0.0.1")

settings = load_settings()
DEVICES = settings.get("devices", DEFAULT_DEVICES)
ACTIVE_DEVICE = settings.get("active", "Sony TV")
TV_IP = DEVICES.get(ACTIVE_DEVICE, "127.0.0.1")

ADB_PATH = r".\platform-tools\adb.exe"
