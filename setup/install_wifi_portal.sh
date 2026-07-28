#!/bin/bash
# setup/install_wifi_portal.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

echo "Installing balena-wifi-connect..."
bash <(curl -L https://github.com/balena-io/wifi-connect/raw/master/scripts/raspbian-install.sh)

echo "Installing systemd service..."
sudo cp "$SCRIPT_DIR/systemd/wmata-wifi-setup.service" /etc/systemd/system/

echo "Enabling wmata-wifi-setup.service on boot..."
sudo systemctl daemon-reload
sudo systemctl enable wmata-wifi-setup.service

echo "Done! The captive portal is now installed."
echo "If your Pi ever boots up and cannot connect to a known Wi-Fi network,"
echo "it will broadcast a hotspot named 'WMATA-Sign-Setup'."
