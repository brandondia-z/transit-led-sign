import os
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_env_path():
    project_root = os.path.dirname(os.path.dirname(__file__))
    secure_env = os.path.join(project_root, ".wmata_secrets.env")
    if os.path.exists(secure_env):
        return secure_env
    return os.path.join(project_root, ".env")

def read_settings():
    settings = {}
    path = get_env_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    settings[k] = v
    return settings

def save_settings(new_settings):
    settings = read_settings()
    settings.update(new_settings)
    path = get_env_path()
    with open(path, "w") as f:
        for k, v in settings.items():
            f.write(f"{k}={v}\n")
    # In a real app we'd signal the main process to reload here
    return True

def scan_wifi():
    try:
        res = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
        networks = []
        for line in res.stdout.splitlines():
            if ":" in line:
                ssid, sig = line.split(":", 1)
                if ssid and ssid not in [n['ssid'] for n in networks]:
                    networks.append({"ssid": ssid, "signal": sig})
        return networks
    except Exception:
        # Fallback for dev on Mac
        return [{"ssid": "MyHomeNetwork", "signal": "80"}, {"ssid": "GuestWiFi", "signal": "40"}]

@app.route("/")
def index():
    settings = read_settings()
    networks = scan_wifi()
    return render_template("index.html", settings=settings, networks=networks)

@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.json
    save_settings({
        "STATION_CODES": data.get("station_codes"),
        "DIRECTION_GROUP": data.get("direction_group"),
        "DISPLAY_MODE": data.get("display_mode"),
        "BRIGHTNESS": data.get("brightness")
    })
    return jsonify({"success": True})

@app.route("/api/wifi", methods=["POST"])
def connect_wifi():
    data = request.json
    ssid = data.get("ssid")
    password = data.get("password")
    try:
        # Attempt connection via NetworkManager
        subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], check=True)
        return jsonify({"success": True, "message": "Connected successfully! Sign will reboot."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
