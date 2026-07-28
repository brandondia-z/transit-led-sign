import time
import requests
import threading
import logging
from src.state import StateManager
from src.models import TrainPrediction, Alert

class WMATAClient:
    API_BASE = "https://api.wmata.com"
    
    DESTINATION_MAP = {
        "New Crlton": "N Carrollton",
        "NEW CARROLLTON": "N Carrollton",
        "Hntingtn": "Huntington",
        "Branch Av": "Branch Ave",
        "Frndshp Hts": "Friendship Ht",
        "FRIENDSHIP HGTS": "Friendship Ht",
        "Silvr Sprg": "Silver Sprg",
        "Grnbelt": "Greenbelt",
        "GREENBELT": "Greenbelt",
        "Shady Grv": "Shady Grove",
        "Wiehle-Rstn": "Wiehle-Restn",
        "Downtwn Lrgo": "Dwntwn Largo",
        "Largo": "Dwntwn Largo",
        "LARGO": "Dwntwn Largo",
        "ASHBURN": "Ashburn",
        "FRAN/SPRING": "Franconia",
        "Franconia": "Franconia",
        "N Bthesda": "N Bethesda",
        "NORTH BETHESDA": "N Bethesda",
        "Vienna": "Vienna",
        "ssenger": "No Passenger"
    }
    
    def __init__(self, state: StateManager):
        self.state = state
        self.session = requests.Session()
        self.session.headers.update({"api_key": state.config.wmata_api_key})
        self.running = False
        self.thread = None
        self._last_alert_fetch = 0
        self.alerts_cache = []

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _poll_loop(self):
        while self.running:
            config = self.state.get_state_snapshot()["config"]
            station_codes = config.station_codes
            if not station_codes or not config.wmata_api_key:
                time.sleep(5)
                continue
                
            try:
                predictions = self._fetch_predictions(station_codes)
                
                # Filter by group if needed
                if config.direction_group != "all":
                    predictions = [p for p in predictions if p.group == config.direction_group]
                
                # Fetch alerts every 60 seconds
                now = time.time()
                if now - self._last_alert_fetch > 60:
                    self.alerts_cache = self._fetch_alerts()
                    self._last_alert_fetch = now
                
                self.state.update_predictions(predictions, self.alerts_cache)
            except Exception as e:
                logging.error(f"WMATA API Error: {e}")
                self.state.set_api_error(True)
                
            # Sleep 20 seconds between API calls to respect rate limits
            # Wait can be instantly interrupted by refresh_event!
            self.state.refresh_event.wait(20)
            self.state.refresh_event.clear()

    def _fetch_predictions(self, station_codes: str) -> list[TrainPrediction]:
        url = f"{self.API_BASE}/StationPrediction.svc/json/GetPrediction/{station_codes}"
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        predictions = []
        for t in data.get("Trains", []):
            # Skip non-revenue trains
            if t.get("Line") == "No" or t.get("Destination") == "Train":
                continue
                
            raw_dest = t.get("Destination", "")
            mapped_dest = self.DESTINATION_MAP.get(raw_dest, raw_dest)
            
            predictions.append(TrainPrediction(
                line=t.get("Line", ""),
                destination=mapped_dest,
                destination_full=t.get("DestinationName", ""),
                minutes=t.get("Min", ""),
                car_count=t.get("Car", ""),
                group=t.get("Group", ""),
                location=t.get("LocationName", "")
            ))
            
        return predictions

    def _fetch_alerts(self) -> list[Alert]:
        url = f"{self.API_BASE}/Incidents.svc/json/Incidents"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            alerts = []
            for inc in data.get("Incidents", []):
                alerts.append(Alert(
                    lines_affected=inc.get("LinesAffected", ""),
                    description=inc.get("Description", "")
                ))
            return alerts
        except Exception:
            return self.alerts_cache # Return existing on failure
