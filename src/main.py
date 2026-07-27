import time
import signal
import sys
import logging
from src.state import StateManager
from src.api_client import WMATAClient
from src.renderer import Renderer
from src.display_modes import compact

logging.basicConfig(level=logging.INFO)

class MainEngine:
    def __init__(self):
        self.state = StateManager()
        self.renderer = Renderer(self.state.config)
        self.api_client = WMATAClient(self.state)
        self.running = False

    def start(self):
        logging.info("Starting WMATA Sign Engine...")
        self.running = True
        
        # Start API polling in background
        self.api_client.start()
        
        # Main render loop
        try:
            while self.running:
                state_snapshot = self.state.get_state_snapshot()
                mode = state_snapshot["config"].display_mode
                
                if mode == "transit":
                    compact.render(self.renderer, state_snapshot)
                else:
                    # Fallback if unknown mode
                    self.renderer.clear()
                    self.renderer.draw_text(self.renderer.font_6x10, 10, 20, "AMBER", f"Mode: {mode}")
                    
                self.renderer.swap()
                time.sleep(0.033) # ~30 fps
                
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        logging.info("Shutting down...")
        self.running = False
        self.api_client.stop()
        self.renderer.clear()
        sys.exit(0)

if __name__ == "__main__":
    engine = MainEngine()
    
    def signal_handler(sig, frame):
        engine.stop()
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    engine.start()
