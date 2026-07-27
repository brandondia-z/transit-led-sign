from dataclasses import dataclass

@dataclass
class TrainPrediction:
    line: str           # e.g., "RD", "BL", "OR"
    destination: str    # e.g., "Shady Gr"
    destination_full: str
    minutes: str        # e.g., "ARR", "BRD", "5", "---"
    car_count: str      # e.g., "8", "6", "-"
    group: str          # "1" or "2"
    location: str       # e.g., "Metro Center"
    
@dataclass
class Alert:
    lines_affected: str
    description: str
