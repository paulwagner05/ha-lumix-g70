# Panasonic Lumix G70 - Home Assistant Integration

A custom integration to seamlessly integrate and control your Panasonic Lumix G70 mirrorless camera directly within Home Assistant over your local network using its native HTTP API (`cam.cgi`).

## Features
* **Config Flow (UI Setup)**: Fully installable via the UI. No `configuration.yaml` editing required!
* **Multiple Devices**: Add as many cameras as you want directly from the Integrations page. Home Assistant automatically creates a dedicated Device and Entities for each camera.
* **Take Photo Button**: Instantly triggers the camera to take a picture using a native Home Assistant Button Entity (`button.press`).
* **Return to Play Mode (Hardware Protection)**: A built-in Switch Entity allows you to toggle the camera's state machine behavior:
  - **Enabled (Default)**: The camera automatically wakes up (`recmode`), takes the photo (`capture`), waits for processing, and forces itself back to sleep (`playmode`). This puts the sensor in standby, preventing thermal overload and extending hardware lifespan.
  - **Disabled**: The camera wakes up, takes the photo, and stops. It skips the processing delay and stays in record mode, ready for consecutive rapid shots.

## Installation

### HACS
1. In Home Assistant, navigate to **HACS > Integrations**.
2. Click the 3 dots in the top right corner and select **Custom repositories**.
3. Paste the URL to this GitHub repository.
4. Select **Integration** as the category and click **Add**.
5. Find the new "Panasonic Lumix G70 Controller" card, click download, and restart Home Assistant.

## Prerequisites & Security
1. **Infrastructure Mode**: The camera must be connected to your home Wi-Fi as a regular client, not serving its own Wi-Fi Access Point.
2. **Static IP**: You must assign a static IP address in your router so the integration can reliably reach the camera.
3. **Network Isolation**: The camera's API has no authentication. It is strongly recommended to isolate the camera on an IoT VLAN and restrict access so that only your Home Assistant server can reach it on TCP Port 80.

## Configuration
1. Go to **Settings > Devices & Services** in Home Assistant.
2. Click **Add Integration** and search for `Panasonic Lumix G70 Controller`.
3. Enter your camera's IP Address.
4. Setup is complete! A new Device will be added with your "Take Photo" button and "Return to Play Mode" switch.