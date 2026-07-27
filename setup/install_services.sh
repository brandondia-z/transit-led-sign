#!/bin/bash
# install_services.sh
# Installs systemd services for the WMATA sign.

set -e

echo "=== Installing Systemd Services ==="

sudo cp systemd/wmata-sign.service /etc/systemd/system/
sudo cp systemd/wifi-portal.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable wmata-sign.service
sudo systemctl enable wifi-portal.service

echo "Services installed and enabled to start on boot."
echo "You can start them manually with:"
echo "  sudo systemctl start wmata-sign"
echo "  sudo systemctl start wifi-portal"
