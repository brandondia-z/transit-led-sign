import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO)

def check_internet():
    try:
        # Ping google DNS to check for active internet connection
        subprocess.check_call(["ping", "-c", "1", "-W", "2", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def start_hotspot():
    logging.info("Starting LED-Sign-Setup hotspot...")
    try:
        # nmcli automatically handles dhcp and dnsmasq for shared hotspots
        subprocess.run([
            "nmcli", "device", "wifi", "hotspot", 
            "ifname", "wlan0", 
            "ssid", "LED-Sign-Setup"
        ], check=True)
        logging.info("Hotspot started successfully!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start hotspot: {e}")

def main():
    # Wait a short bit after boot for NetworkManager to try connecting
    logging.info("Waiting 10 seconds for normal wifi connection...")
    time.sleep(10)
    
    while True:
        if not check_internet():
            logging.info("No internet detected! Launching hotspot.")
            start_hotspot()
            # Sleep for a long time after starting the hotspot so we don't spam it
            time.sleep(600)
        else:
            # Check every 10 seconds
            time.sleep(10)

if __name__ == "__main__":
    main()
