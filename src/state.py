import threading
from src.config import load_config
from src.models import TrainPrediction, Alert

class StateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.config = load_config()
        self.predictions: list[TrainPrediction] = []
        self.alerts: list[Alert] = []
        self.api_error: bool = False
        self.has_connected_once: bool = False
        
        # UI Fetching States
        self.refresh_event = threading.Event()
        self.is_fetching = False
        self.fetching_station_name = ""
        self.fetching_direction_name = ""
        
    def update_predictions(self, predictions: list[TrainPrediction], alerts: list[Alert] = None):
        with self._lock:
            self.predictions = predictions
            if alerts is not None:
                self.alerts = alerts
            self.api_error = False
            self.has_connected_once = True
            self.is_fetching = False
            
    def set_api_error(self, is_error: bool):
        with self._lock:
            self.api_error = is_error
            
    def update_config(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self.config, k):
                    # Only convert to int if it's brightness
                    if k == "brightness":
                        setattr(self.config, k, int(v))
                    else:
                        setattr(self.config, k, v)
            self.config.save_to_json()
                    
    def trigger_refresh(self, station_name: str, direction_name: str):
        with self._lock:
            self.fetching_station_name = station_name
            self.fetching_direction_name = direction_name
            self.is_fetching = True
            self.predictions = [] # Clear the board!
        self.refresh_event.set()
        
    def get_state_snapshot(self):
        with self._lock:
            # Return a shallow copy of lists so the renderer can iterate safely
            return {
                "config": self.config,
                "predictions": list(self.predictions),
                "alerts": list(self.alerts),
                "api_error": self.api_error,
                "has_connected_once": self.has_connected_once,
                "is_fetching": self.is_fetching,
                "fetching_station_name": self.fetching_station_name,
                "fetching_direction_name": self.fetching_direction_name
            }
