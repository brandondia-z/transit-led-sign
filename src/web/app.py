import os
import requests
from flask import Flask, render_template, jsonify, request, redirect
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
        
    @app.route("/api/canvas", methods=["POST"])
    def update_canvas():
        data = request.json
        if "canvas_data" in data:
            state.update_config(canvas_data=data["canvas_data"])
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

    @app.before_request
    def intercept_captive_portal():
        # If the request is meant for Apple/Android captive portal checks
        # The Host header won't be our IP or local hostname
        host = request.host.split(':')[0]
        if host not in ["10.42.0.1", "led-sign.local", "localhost", "127.0.0.1"]:
            # Redirect to the wifi page!
            return redirect("http://10.42.0.1/wifi")

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
            ssids = [s for s in ssids if s and s != "LED-Sign-Setup"]
            return jsonify(ssids)
        except Exception as e:
            return jsonify([])

    last_wifi_error = None

    @app.route("/api/wifi/status", methods=["GET"])
    def wifi_status():
        nonlocal last_wifi_error
        if last_wifi_error:
            err = last_wifi_error
            last_wifi_error = None
            return jsonify({"status": "failed", "error": err})
        return jsonify({"status": "waiting"})

    @app.route("/api/wifi/connect", methods=["POST"])
    def connect_wifi():
        nonlocal last_wifi_error
        import subprocess
        import threading
        import time
        
        data = request.json
        ssid = data.get("ssid")
        password = data.get("password")
        
        last_wifi_error = None
        
        def attempt_connection():
            nonlocal last_wifi_error
            time.sleep(1) # Allow the HTTP response to reach the phone first
            cmd = ["sudo", "nmcli", "device", "wifi", "connect", ssid, "password", password]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                last_wifi_error = "Incorrect password or network out of range."
                
        threading.Thread(target=attempt_connection).start()
        return jsonify({"status": "testing"})

    return app
