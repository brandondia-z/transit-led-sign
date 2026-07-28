import time
import signal
import sys
import subprocess
from src.state import StateManager
from src.renderer import Renderer
from src.display_modes import compact
from src.models import TrainPrediction
from src.utils import check_and_stop_service, restart_service

def main():
    service_was_stopped = check_and_stop_service()
    
    print("\nStarting WMATA Demo Mode...")
    print("Press Ctrl+C to exit.")
    
    state = StateManager()
    renderer = Renderer(state.config)
    
    # Combinations covering every possible color, line, and edge case!
    combos = [
        [
            TrainPrediction(line="RD", destination="Shady Grove", destination_full="Shady Grove", minutes="BRD", car_count="8", group="1", location=""),
            TrainPrediction(line="RD", destination="Glenmont", destination_full="Glenmont", minutes="1", car_count="6", group="1", location=""),
            TrainPrediction(line="RD", destination="Silver Spring", destination_full="Silver Spring", minutes="5", car_count="-", group="1", location="")
        ],
        [
            TrainPrediction(line="OR", destination="Vienna", destination_full="Vienna", minutes="ARR", car_count="8", group="1", location=""),
            TrainPrediction(line="OR", destination="New Crlton", destination_full="New Carrollton", minutes="3", car_count="6", group="1", location=""),
            TrainPrediction(line="No", destination="No Passenger", destination_full="No Passenger", minutes="---", car_count="-", group="1", location="")
        ],
        [
            TrainPrediction(line="BL", destination="Franconia", destination_full="Franconia-Springfield", minutes="2", car_count="6", group="1", location=""),
            TrainPrediction(line="BL", destination="Largo", destination_full="Largo", minutes="6", car_count="6", group="1", location=""),
            TrainPrediction(line="BL", destination="Huntington", destination_full="Huntington", minutes="12", car_count="8", group="1", location="")
        ],
        [
            TrainPrediction(line="GR", destination="Greenbelt", destination_full="Greenbelt", minutes="BRD", car_count="8", group="1", location=""),
            TrainPrediction(line="GR", destination="Branch Ave", destination_full="Branch Ave", minutes="4", car_count="8", group="1", location=""),
            TrainPrediction(line="GR", destination="College Park", destination_full="College Park", minutes="15", car_count="6", group="1", location="")
        ],
        [
            TrainPrediction(line="YL", destination="Huntington", destination_full="Huntington", minutes="ARR", car_count="6", group="1", location=""),
            TrainPrediction(line="YL", destination="Mt Vernon", destination_full="Mt Vernon Sq", minutes="5", car_count="8", group="1", location=""),
            TrainPrediction(line="YL", destination="Fort Totten", destination_full="Fort Totten", minutes="22", car_count="6", group="1", location="")
        ],
        [
            TrainPrediction(line="SV", destination="Ashburn", destination_full="Ashburn", minutes="BRD", car_count="8", group="1", location=""),
            TrainPrediction(line="SV", destination="Largo", destination_full="Largo", minutes="3", car_count="6", group="1", location=""),
            TrainPrediction(line="SV", destination="Wiehle-Reston", destination_full="Wiehle-Reston East", minutes="9", car_count="8", group="1", location="")
        ]
    ]
    
    def signal_handler(sig, frame):
        renderer.clear()
        print("\nDemo stopped.")
        if service_was_stopped:
            restart_service()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        for preds in combos:
            # Mock the state predictions
            state.update_predictions(preds, [])
            state_snapshot = state.get_state_snapshot()
            
            # Render this frame for 4 seconds (at ~30fps)
            start_time = time.time()
            while time.time() - start_time < 4:
                compact.render(renderer, state_snapshot)
                renderer.swap()
                time.sleep(0.033)

if __name__ == "__main__":
    main()
