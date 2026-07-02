# Universal Remote

Universal Remote is a powerful, Python-based desktop application designed to let you seamlessly control Android devices and Smart TVs over your local network using ADB (Android Debug Bridge). 

## 🌟 Features
- **Wireless Connection**: Connect to your Android TV or phone over Wi-Fi without needing a USB cable.
- **Full Remote Control**: Send native Android key events (Home, Back, Power, Volume up/down, D-Pad navigation, etc.) directly from your computer.
- **Device Management**: Easily switch between multiple connected devices.
- **Standalone Executable**: Run the application instantly from the `dist/` folder without needing to install Python.

## 🚀 Getting Started

### Running the App
The easiest way to use the app is to double-click the pre-compiled executable located in the `dist` folder:
`dist/UniversalRemote.exe`

### Running from Source
If you want to run the application from the source code:
1. Ensure you have Python 3 installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```bash
   python Remote.py
   ```

## 🔧 How to Use
1. Open the application and navigate to the connection settings.
2. Enter the IP Address of your Android TV or device (make sure Developer Options and Wireless Debugging are enabled on the TV).
3. Click **Connect**.
4. Use the on-screen buttons to control your TV!

## ⚠️ Requirements
- Both your PC and the Android device must be on the **same Wi-Fi network**.
- **Wireless Debugging** must be enabled on the target Android device.

## ⚖️ License
This project is proprietary and closed-source. See the `LICENSE` file for more details.
