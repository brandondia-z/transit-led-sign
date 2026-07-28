import os
from dataclasses import dataclass
from dotenv import load_dotenv

import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

@dataclass
class Config:
    wmata_api_key: str
    station_codes: str
    direction_group: str
    display_mode: str
    brightness: int
    gpio_mapping: str
    gpio_slowdown: int
    scroll_speed_ms: int
    canvas_data: list

    def save_to_json(self):
        # We only save user-configurable settings, not secrets like api key
        data = {
            "station_codes": self.station_codes,
            "direction_group": self.direction_group,
            "display_mode": self.display_mode,
            "brightness": self.brightness,
            "canvas_data": self.canvas_data
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

def load_config() -> Config:
    # Look for the secrets file in the project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    secure_env = os.path.join(project_root, ".wmata_secrets.env")
    
    if os.path.exists(secure_env):
        load_dotenv(secure_env)
    else:
        # Fallback to standard .env
        load_dotenv(os.path.join(project_root, ".env"))

    # Load persistent JSON config if it exists
    json_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                json_data = json.load(f)
        except Exception:
            pass

    return Config(
        wmata_api_key=os.getenv("WMATA_API_KEY", ""),
        station_codes=json_data.get("station_codes", os.getenv("STATION_CODES", "A01,C01")),
        direction_group=json_data.get("direction_group", os.getenv("DIRECTION_GROUP", "all")),
        display_mode=json_data.get("display_mode", os.getenv("DISPLAY_MODE", "transit")),
        brightness=int(json_data.get("brightness", os.getenv("BRIGHTNESS", "60"))),
        gpio_mapping=os.getenv("GPIO_MAPPING", "regular"),
        gpio_slowdown=int(os.getenv("GPIO_SLOWDOWN", "1")),
        scroll_speed_ms=int(os.getenv("SCROLL_SPEED_MS", "30")),
        canvas_data=json_data.get("canvas_data", [])
    )
