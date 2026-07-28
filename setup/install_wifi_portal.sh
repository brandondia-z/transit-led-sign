#!/bin/bash
# setup/install_wifi_portal.sh

echo "Installing balena-wifi-connect..."
curl -sL https://github.com/balena-os/wifi-connect/raw/master/scripts/Install.sh | bash

echo "Installing systemd service..."
sudo cp systemd/wmata-wifi-setup.service /etc/systemd/system/

echo "Enabling wmata-wifi-setup.service on boot..."
sudo systemctl daemon-reload
sudo systemctl enable wmata-wifi-setup.service

echo "Done! The captive portal is now installed."
echo "If your Pi ever boots up and cannot connect to a known Wi-Fi network,"
echo "it will broadcast a hotspot named 'WMATA-Sign-Setup'."
