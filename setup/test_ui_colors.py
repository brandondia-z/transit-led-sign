#!/usr/bin/env python3
"""
UI Color and Layout Test Script
This script cycles through every Line color, Car length, and Status combination
on the physical LED matrix so you can visually inspect the colors and spacing.

Usage: sudo ~/wmata_env/bin/python setup/test_ui_colors.py
"""

import time
import sys
import signal

# Add parent directory to path so we can import src modules
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import StateManager
from src.renderer import Renderer
from src.display_modes import compact
from src.models import TrainPrediction
from src.utils import check_and_stop_service, restart_service

def main():
    service_was_stopped = check_and_stop_service()
    
    print("\nStarting UI Color Test on LED Matrix...")
    print("Press Ctrl+C to exit.")
    
    state = StateManager()
    renderer = Renderer(state.config)
    
    # We will generate frames covering all edge cases
    
    lines = [
        ("RD", "Shady Grove"), 
        ("OR", "Vienna"), 
        ("BL", "Franconia"), 
        ("GR", "Greenbelt"), 
        ("YL", "Huntington"), 
        ("SV", "Ashburn")
    ]
    
    statuses = ["BRD", "ARR", "1", "15", "---"]
    cars = ["6", "8", "-"]
    
    # Build some pages of predictions
    pages = []
    
    # Page 1: Every line color with typical arrivals
    page1 = []
    for line, dest in lines:
        page1.append(TrainPrediction(line=line, destination=dest, destination_full=dest, minutes="5", car_count="8", group="1", location=""))
    pages.append(page1)
    
    # Page 2: Every line color with BRD / ARR and short cars
    page2 = []
    for line, dest in lines:
        status = "BRD" if line in ["RD", "BL", "YL"] else "ARR"
        page2.append(TrainPrediction(line=line, destination=dest, destination_full=dest, minutes=status, car_count="6", group="1", location=""))
    pages.append(page2)
    
    # Page 3: Edge cases and weird lengths
    page3 = [
        TrainPrediction(line="No", destination="No Passenger", destination_full="No Passenger", minutes="---", car_count="-", group="1", location=""),
        TrainPrediction(line="RD", destination="Dwntwn Largo", destination_full="Downtown Largo", minutes="BRD", car_count="8", group="1", location=""),
        TrainPrediction(line="GR", destination="Friendship Ht", destination_full="Friendship Heights", minutes="ARR", car_count="6", group="1", location=""),
        TrainPrediction(line="BL", destination="Mt Vernon Sq", destination_full="Mt Vernon Sq", minutes="12", car_count="8", group="1", location=""),
        TrainPrediction(line="SV", destination="Wiehle-Restn", destination_full="Wiehle-Reston East", minutes="2", car_count="6", group="1", location=""),
        TrainPrediction(line="OR", destination="N Carrollton", destination_full="New Carrollton", minutes="15", car_count="8", group="1", location=""),
    ]
    pages.append(page3)
    
    def signal_handler(sig, frame):
        renderer.clear()
        print("\nTest stopped.")
        if service_was_stopped:
            restart_service()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    page_idx = 0
    while True:
        preds = pages[page_idx % len(pages)]
        
        # Override state predictions
        state.update_predictions(preds, [])
        state_snapshot = state.get_state_snapshot()
        
        # Render this frame for 4 seconds at 30fps
        start_time = time.time()
        while time.time() - start_time < 4:
            compact.render(renderer, state_snapshot)
            renderer.swap()
            time.sleep(0.033)
            
        page_idx += 1

if __name__ == "__main__":
    main()
