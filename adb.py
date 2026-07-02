import subprocess
import config

def run_adb(*args):
    """Helper to run adb commands without showing cmd window on Windows"""
    try:
        # CREATE_NO_WINDOW = 0x08000000
        return subprocess.run(
            [config.ADB_PATH, *args], 
            capture_output=True, 
            text=True, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        print(f"ADB Error: {e}")
        return None

def connect():
    run_adb("connect", config.TV_IP)

def disconnect():
    run_adb("disconnect", config.TV_IP)

def is_connected():
    res = run_adb("devices")
    if res and config.TV_IP in res.stdout:
        # Check if it actually says "device" and not "offline"
        # Example output: "10.33.225.16:5555	device"
        parts = res.stdout.split(config.TV_IP)
        if len(parts) > 1 and "device" in parts[1].split()[0]:
            return True
    return False

def key(code):
    run_adb("shell", "input", "keyevent", str(code))

def input_text(text):
    # Escape spaces as %s for ADB
    escaped_text = text.replace(" ", "%s")
    # Escape single quotes for the android shell
    escaped_text = escaped_text.replace("'", "'\\''")
    
    # We pass the string wrapped in single quotes to the android shell
    run_adb("shell", "input", "text", f"'{escaped_text}'")

def launch_app(packages):
    """Try to launch a package. If a list is provided, try them in order until one succeeds."""
    if isinstance(packages, str):
        packages = [packages]
        
    for pkg in packages:
        res = run_adb("shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")
        # monkey prints "monkey aborted" or "No activities found" if it fails.
        if res and "monkey aborted" not in res.stdout and "No activities found" not in res.stdout:
            # Likely successful
            break

def open_url(url):
    run_adb("shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url)

KEYS = {
    "HOME": 3,
    "BACK": 4,
    "UP": 19,
    "DOWN": 20,
    "LEFT": 21,
    "RIGHT": 22,
    "OK": 23,
    "VOL_UP": 24,
    "VOL_DOWN": 25,
    "MUTE": 164,
    "RECENTS": 187,
    "SETTINGS": 176,
    "PLAY_PAUSE": 85,
    "NEXT": 87,
    "PREVIOUS": 88,
    "SEARCH": 84,
    "DEL": 67, # Backspace
}