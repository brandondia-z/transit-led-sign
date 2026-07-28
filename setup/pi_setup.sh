#!/bin/bash
# pi_setup.sh
# Run this script on your Raspberry Pi to install all dependencies for the LED sign.
# Usage: ./pi_setup.sh

set -e

echo "=== Updating System ==="
sudo apt-get update
sudo apt-get upgrade -y

echo "=== Installing Dependencies ==="
sudo apt-get install -y build-essential python3-dev python3-pip python3-venv python3-pillow cython3 git libgpiod-dev

echo "=== Blacklisting Onboard Audio (snd_bcm2835) ==="
# This prevents DMA timing collisions with the LED matrix driver
cat <<EOF | sudo tee /etc/modprobe.d/matrix-blacklist.conf
blacklist snd_bcm2835
EOF

echo "=== Installing hzeller/rpi-rgb-led-matrix ==="
cd ~
if [ ! -d "rpi-rgb-led-matrix" ]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
fi
cd rpi-rgb-led-matrix
# Build the main C++ library
make
echo "=== Setting up Python Virtual Environment ==="
cd ~
if [ ! -d "wmata_env" ]; then
    # Must use --system-site-packages so it sees globally installed modules if needed
    python3 -m venv --system-site-packages wmata_env
fi

echo "=== Installing Python Bindings ==="
# The new build system requires running pip install from the root of the repository
cd ~/rpi-rgb-led-matrix
# Ensure cmake is installed as it's required by the new build system
sudo apt-get install -y cmake
# Install the rgbmatrix bindings into our venv
~/wmata_env/bin/python -m pip install .

echo "=== Installing Python Packages ==="
~/wmata_env/bin/python -m pip install requests python-dotenv flask

echo "=== Setup Complete ==="
echo "Note: The audio blacklist requires a reboot to take effect fully."
echo "Please reboot your Pi (sudo reboot) and then run the hardware test script."
