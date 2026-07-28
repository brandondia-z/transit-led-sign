import subprocess
import sys

def check_and_stop_service():
    try:
        result = subprocess.run(['systemctl', 'is-active', '--quiet', 'wmata-sign.service'])
        if result.returncode == 0:
            print("WARNING: The wmata-sign.service is currently running in the background!")
            print("Running this script at the same time will cause hardware conflicts and crash the LED matrix.")
            resp = input("Do you want to stop the service now? [Y/n]: ").strip().lower()
            if resp == '' or resp == 'y':
                print("Stopping wmata-sign.service...")
                subprocess.run(['sudo', 'systemctl', 'stop', 'wmata-sign.service'], check=True)
                print("Service stopped.")
                return True
            else:
                print("Cannot safely run while service is active. Exiting.")
                sys.exit(1)
    except Exception as e:
        print(f"Notice: Could not check systemd service status: {e}")
    return False

def restart_service():
    resp = input("\nDo you want to restart the background WMATA sign service? [Y/n]: ").strip().lower()
    if resp == '' or resp == 'y':
        print("Starting wmata-sign.service...")
        subprocess.run(['sudo', 'systemctl', 'start', 'wmata-sign.service'])
        print("Service started!")
