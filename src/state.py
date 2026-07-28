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
        
    def update_predictions(self, predictions: list[TrainPrediction], alerts: list[Alert] = None):
        with self._lock:
            self.predictions = predictions
            if alerts is not None:
                self.alerts = alerts
            self.api_error = False
            self.has_connected_once = True
            
    def set_api_error(self, is_error: bool):
        with self._lock:
            self.api_error = is_error
            
    def update_config(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                if hasattr(self.config, k):
                    setattr(self.config, k, v)
                    
    def get_state_snapshot(self):
        with self._lock:
            # Return a shallow copy of lists so the renderer can iterate safely
            return {
                "config": self.config,
                "predictions": list(self.predictions),
                "alerts": list(self.alerts),
                "api_error": self.api_error,
                "has_connected_once": self.has_connected_once
            }
