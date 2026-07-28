#!/bin/bash
# setup/install_wifi_portal.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

echo "Uninstalling old balena-wifi-connect (if exists)..."
sudo systemctl stop wmata-wifi-setup.service 2>/dev/null
sudo systemctl disable wmata-wifi-setup.service 2>/dev/null
sudo rm -f /etc/systemd/system/wmata-wifi-setup.service
sudo rm -f /usr/local/sbin/wifi-connect
sudo rm -rf /usr/local/share/wifi-connect

echo "Setting up NetworkManager captive portal DNS..."
sudo mkdir -p /etc/NetworkManager/dnsmasq-shared.d/
echo "address=/#/10.42.0.1" | sudo tee /etc/NetworkManager/dnsmasq-shared.d/captive_portal.conf > /dev/null

echo "Installing custom WMATA Wi-Fi Manager systemd service..."
sudo cp "$SCRIPT_DIR/systemd/wmata-wifi-manager.service" /etc/systemd/system/

echo "Enabling wmata-wifi-manager.service on boot..."
sudo systemctl daemon-reload
sudo systemctl enable wmata-wifi-manager.service

echo "Done! The captive hotspot is now installed."
echo "If your Pi ever boots up and cannot connect to a known Wi-Fi network,"
echo "it will broadcast an open hotspot named 'LED-Sign-Setup'."
echo "Connect to it, then open http://led-sign.local/wifi in your browser."
