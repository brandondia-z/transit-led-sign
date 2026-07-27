# WMATA LED Arrival Sign

A standalone, custom-built LED arrival sign replicating the official WMATA PIDS displays, powered by a Raspberry Pi and RGB LED matrix panels.

This project pulls real-time transit data directly from the official WMATA API, formats the predictions, and renders them in a multi-train layout similar to real Metro station platforms. It is designed to run headless as a "turn-key" appliance.

## Features

- **Real-Time Data:** Polls the WMATA API for live train arrivals and statuses (ARR, BRD).
- **Authentic Styling:** Recreates the exact WMATA amber typography, blinking arrival indicators, and full-color line badges (Red, Blue, Orange, Silver, Yellow, Green).
- **Web Dashboard:** Access `http://led-sign.local` on your phone to configure the target station, filter directions, toggle between Train/Clock modes, and adjust brightness.
- **Wi-Fi Provisioning:** If the sign loses internet, it broadcasts its own setup Wi-Fi network so you can enter new network credentials via a captive portal.

---

## Hardware Architecture

1. **Controller:** Raspberry Pi 3B+ (or Pi 4). Raspberry Pi OS Lite (32-bit Bookworm) is highly recommended for maximum stability and performance.
2. **Display Panels:** 2x 64x32 P2.5 RGB Full Color LED Matrix Panels (HUB75 interface). Daisy-chained horizontally for a 128x32 total resolution.
3. **Interface Adapter:** A HUB75 adapter HAT (e.g., Adafruit RGB Matrix HAT or WT-RGBA Seengreat Matrix Board) connecting the Pi's 40-pin GPIO to the first panel's Data IN port.
4. **Power Supply:** 5V / 4A power adapter. Because the matrix can draw a huge amount of current (up to 8A at full white brightness), the software limits the maximum brightness to ~40-50% to prevent Pi brownouts.

## Setup & Installation

### 1. API Keys & Configuration
You must obtain a free developer API key from the [WMATA Developer Portal](https://developer.wmata.com/). 

Create a file named `.wmata_secrets.env` in the root of the project directory (ensure this remains in `.gitignore`):

```env
WMATA_API_KEY=your_key_here
```

### 2. Install Dependencies
Run the included Pi setup script. This installs necessary system packages, blacklists the onboard audio (which conflicts with the matrix DMA timings), and builds the `hzeller/rpi-rgb-led-matrix` C++ library and Python bindings.

```bash
chmod +x setup/pi_setup.sh
./setup/pi_setup.sh
sudo reboot
```

### 3. Hardware Validation
Because different HATs require different GPIO mappings (e.g., `regular` vs `adafruit-hat`) and different Pi models require different slowdown parameters (e.g., `1` for Pi 3B+, `2` or `3` for Pi 4), run the hardware test script to find your correct settings:

```bash
sudo ~/wmata_env/bin/python setup/test_matrix.py --mapping="regular" --slowdown=1
```
*(If the colors look scrambled or glitchy, press Ctrl+C and try a different mapping or slowdown value).*

### 4. Running the Engine
Start the application manually:
```bash
sudo ~/wmata_env/bin/python src/main.py
```
*(Note: `sudo` is strictly required as the library directly maps hardware memory for the GPIO timings).*

### 5. Install Systemd Services
To have the sign start automatically when the Pi boots up:
```bash
chmod +x setup/install_services.sh
./setup/install_services.sh
```

This installs two services:
- `wmata-sign.service` (The display engine)
- `wifi-portal.service` (The configuration web portal)

## Architecture

- **Main Engine (`src/main.py`):** Runs a 30fps drawing loop, pulling data from the `StateManager`.
- **API Client (`src/api_client.py`):** Runs on a background thread polling WMATA every 20 seconds.
- **Web Portal (`wifi_portal/portal_server.py`):** A Flask web application that modifies the global state on-the-fly without requiring a restart.
