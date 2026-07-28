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
    logging.info("Starting WMATA-Sign-Setup hotspot...")
    try:
        # nmcli automatically handles dhcp and dnsmasq for shared hotspots
        subprocess.run([
            "nmcli", "device", "wifi", "hotspot", 
            "ifname", "wlan0", 
            "ssid", "WMATA-Sign-Setup", 
            "password", "transit123"
        ], check=True)
        logging.info("Hotspot started successfully!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start hotspot: {e}")

def main():
    # Wait a bit after boot for NetworkManager to try connecting to known networks
    logging.info("Waiting 30 seconds for normal wifi connection...")
    time.sleep(30)
    
    if not check_internet():
        logging.info("No internet detected! Launching hotspot.")
        start_hotspot()
    else:
        logging.info("Internet connection is active. WiFi Manager exiting.")

if __name__ == "__main__":
    main()
