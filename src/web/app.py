import os
import requests
from flask import Flask, render_template, jsonify, request
from src.state import StateManager

def create_app(state: StateManager):
    app = Flask(__name__)
    
    stations_cache = None
    lines_cache = None
    
    @app.route("/")
    def index():
        return render_template("index.html")
        
    @app.route("/api/config", methods=["GET"])
    def get_config():
        return jsonify({
            "station_codes": state.config.station_codes,
            "direction_group": state.config.direction_group,
            "display_mode": state.config.display_mode,
            "brightness": state.config.brightness
        })
        
    @app.route("/api/config", methods=["POST"])
    def save_config():
        data = request.json
        state.update_config(
            station_codes=data.get("station_codes", state.config.station_codes),
            direction_group=data.get("direction_group", state.config.direction_group),
            display_mode=data.get("display_mode", state.config.display_mode),
            brightness=data.get("brightness", state.config.brightness)
        )
        
        # Trigger an instant reload of the API data with loading screen!
        state.trigger_refresh(
            station_name=data.get("station_name", "Station"),
            direction_name=data.get("direction_name", "All Destinations")
        )
        return jsonify({"status": "success"})
        
    @app.route("/api/stations", methods=["GET"])
    def get_stations():
        nonlocal stations_cache
        if stations_cache:
            return jsonify(stations_cache)
            
        api_key = state.config.wmata_api_key
        if not api_key:
            return jsonify({"error": "No API key configured"}), 400
            
        try:
            resp = requests.get(
                "https://api.wmata.com/Rail.svc/json/jStations",
                headers={"api_key": api_key},
                timeout=10
            )
            resp.raise_for_status()
            stations_cache = resp.json().get("Stations", [])
            return jsonify(stations_cache)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    @app.route("/api/lines", methods=["GET"])
    def get_lines():
        nonlocal lines_cache
        if lines_cache:
            return jsonify(lines_cache)
            
        api_key = state.config.wmata_api_key
        if not api_key:
            return jsonify({"error": "No API key configured"}), 400
            
        try:
            resp = requests.get(
                "https://api.wmata.com/Rail.svc/json/jLines",
                headers={"api_key": api_key},
                timeout=10
            )
            resp.raise_for_status()
            lines_cache = resp.json().get("Lines", [])
            return jsonify(lines_cache)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/wifi", methods=["GET"])
    def wifi_page():
        return render_template("wifi.html")
        
    @app.route("/api/wifi/scan", methods=["GET"])
    def scan_wifi():
        import subprocess
        try:
            output = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "dev", "wifi", "list"]).decode("utf-8")
            ssids = list(set([line.strip() for line in output.split('\n') if line.strip()]))
            # Remove empty ssids or the hotspot itself
            ssids = [s for s in ssids if s and s != "WMATA-Sign-Setup"]
            return jsonify(ssids)
        except Exception as e:
            return jsonify([])

    @app.route("/api/wifi/connect", methods=["POST"])
    def connect_wifi():
        import subprocess
        data = request.json
        ssid = data.get("ssid")
        password = data.get("password")
        
        try:
            # We must use Popen to not block the response while network drops
            cmd = f"sudo nmcli device wifi connect '{ssid}' password '{password}'"
            subprocess.Popen(cmd, shell=True)
            return jsonify({"status": "connecting"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
