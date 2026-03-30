# Panasonic Lumix G70 - Home Assistant Integration

A lightweight custom integration to control a Panasonic Lumix G70 mirrorless camera over the local network using its native HTTP API (`cam.cgi`).

## Features
* **Take Photo Service (`lumix_g70.take_photo`)**: Triggers the camera to take a picture.
* **Built-in Hardware Protection**: The integration automatically manages the camera's state machine. It wakes the camera up (`recmode`), takes the photo (`capture`), and immediately forces it back to sleep (`playmode`). This closes the mechanical shutter, retracts the lens, and puts the heat-sensitive sensor in standby to prevent thermal overload and extend hardware lifespan.

## Prerequisites
1. **Infrastructure Mode**: The camera must be connected to your home Wi-Fi as a regular client (Infrastructure Mode), not serve it's own Wi-Fi as an Access Point.
2. **Static IP**: You must assign a static IP address (infinite DHCP-Lease) to the camera in your router's DHCP settings so the integration can reliably reach the camera.
3. **Network Isolation (Security)**: The camera's API has absolutely no authentication. It is strongly recommended to isolate the camera in a dedicated IoT VLAN and restrict access so that only your Home Assistant instance can reach it on TCP Port 80.

## Installation
1. Copy the `lumix_g70` folder into your Home Assistant `custom_components` directory.
2. Add the following configuration to your `configuration.yaml` file, and replace `X.X.X.X` with your camera's IP:

```yaml
lumix_g70:
  ip_address: "X.X.X.X"