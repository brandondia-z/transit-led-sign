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

# Keep track of our custom dnsmasq process
dnsmasq_proc = None

def stop_hotspot():
    global dnsmasq_proc
    if dnsmasq_proc:
        logging.info("Stopping custom dnsmasq...")
        dnsmasq_proc.terminate()
        dnsmasq_proc = None

def start_hotspot():
    global dnsmasq_proc
    logging.info("Starting LED-Sign-Setup hotspot...")
    try:
        # Delete any existing profile to start fresh
        subprocess.run(["nmcli", "con", "delete", "LED-Sign-Setup"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        # Create an open AP profile
        subprocess.run([
            "nmcli", "con", "add", 
            "type", "wifi", 
            "ifname", "wlan0", 
            "con-name", "LED-Sign-Setup", 
            "ssid", "LED-Sign-Setup"
        ], check=True, stdout=subprocess.DEVNULL)
        
        # Use manual IPv4 to prevent NetworkManager from locking down DNS
        subprocess.run([
            "nmcli", "con", "modify", "LED-Sign-Setup", 
            "802-11-wireless.mode", "ap", 
            "ipv4.method", "manual",
            "ipv4.addresses", "10.42.0.1/24",
            "ipv4.gateway", "10.42.0.1"
        ], check=True)
        
        # Explicitly remove security just in case NetworkManager defaults to WEP/WPA
        subprocess.run([
            "nmcli", "con", "modify", "LED-Sign-Setup", "remove", "wifi-sec"
        ], stderr=subprocess.DEVNULL)
        
        # Bring the hotspot up
        subprocess.run(["nmcli", "con", "up", "LED-Sign-Setup"], check=True)
        
        # Kill any lingering dnsmasq processes to free port 53
        subprocess.run(["sudo", "killall", "dnsmasq"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        # Start our custom dnsmasq!
        logging.info("Starting captive portal dnsmasq...")
        dnsmasq_proc = subprocess.Popen([
            "sudo", "dnsmasq", 
            "--no-daemon", 
            "--interface=wlan0", 
            "--dhcp-range=10.42.0.10,10.42.0.250,12h", 
            "--address=/#/10.42.0.1"
        ])
        
        logging.info("Hotspot started successfully with True Captive Portal!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start hotspot: {e}")

def main():
    logging.info("WMATA Wi-Fi Manager started.")
    time.sleep(10) # Wait for initial boot connection attempt
    
    was_connected = True
    
    while True:
        connected = check_internet()
        
        if not connected and was_connected:
            logging.info("No internet detected. Starting setup hotspot...")
            start_hotspot()
            was_connected = False
            
        elif connected and not was_connected:
            logging.info("Internet restored. Stopping hotspot processes...")
            stop_hotspot()
            was_connected = True
            
        time.sleep(10)

if __name__ == "__main__":
    main()
