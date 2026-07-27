import os
from dataclasses import dataclass
from dotenv import load_dotenv

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

def load_config() -> Config:
    # Look for the secrets file in the project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    secure_env = os.path.join(project_root, ".wmata_secrets.env")
    
    if os.path.exists(secure_env):
        load_dotenv(secure_env)
    else:
        # Fallback to standard .env
        load_dotenv(os.path.join(project_root, ".env"))

    # Brightness should be capped for safety on 5V/4A
    raw_brightness = int(os.getenv("BRIGHTNESS", "40"))
    safe_brightness = min(raw_brightness, 50)

    return Config(
        wmata_api_key=os.getenv("WMATA_API_KEY", ""),
        station_codes=os.getenv("STATION_CODES", "A01,C01"),
        direction_group=os.getenv("DIRECTION_GROUP", "all"),
        display_mode=os.getenv("DISPLAY_MODE", "transit"),
        brightness=safe_brightness,
        gpio_mapping=os.getenv("GPIO_MAPPING", "regular"),
        gpio_slowdown=int(os.getenv("GPIO_SLOWDOWN", "1")),
        scroll_speed_ms=int(os.getenv("SCROLL_SPEED_MS", "30"))
    )
