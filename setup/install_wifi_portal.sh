#!/bin/bash
# setup/install_wifi_portal.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

echo "Installing balena-wifi-connect..."

ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    URL="https://github.com/balena-io/wifi-connect/releases/download/v4.4.6/wifi-connect-v4.4.6-linux-aarch64.tar.gz"
elif [ "$ARCH" = "armv7l" ]; then
    # For Pi 2/3/4 running 32-bit (Bookworm)
    URL="https://github.com/balena-io/wifi-connect/releases/download/v4.4.6/wifi-connect-v4.4.6-linux-armv7hf.tar.gz"
else
    # Fallback for Pi 1/Zero (armv6l)
    URL="https://github.com/balena-io/wifi-connect/releases/download/v4.4.6/wifi-connect-v4.4.6-linux-rpi.tar.gz"
fi

echo "Downloading $URL..."
TMP_DIR=$(mktemp -d)
curl -Ls "$URL" | tar -xz -C "$TMP_DIR"

sudo mv "$TMP_DIR/wifi-connect" /usr/local/sbin/
sudo mkdir -p /usr/local/share/wifi-connect/
sudo rm -rf /usr/local/share/wifi-connect/ui
sudo mv "$TMP_DIR/ui" /usr/local/share/wifi-connect/ui
rm -rf "$TMP_DIR"

echo "Installing systemd service..."
sudo cp "$SCRIPT_DIR/systemd/wmata-wifi-setup.service" /etc/systemd/system/

echo "Enabling wmata-wifi-setup.service on boot..."
sudo systemctl daemon-reload
sudo systemctl enable wmata-wifi-setup.service

echo "Done! The captive portal is now installed."
echo "If your Pi ever boots up and cannot connect to a known Wi-Fi network,"
echo "it will broadcast a hotspot named 'WMATA-Sign-Setup'."
