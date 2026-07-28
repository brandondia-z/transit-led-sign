import os

# Display Constants
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 32

# WMATA Official Line Colors (Hardware Optimized for LED Panels)
LINE_COLORS = {
    "RD": (255, 0, 0),        # Pure Red
    "BL": (50, 150, 255),     # Brighter Blue
    "OR": (255, 128, 0),      # Pure Orange (no blue to prevent pinkish hue)
    "GR": (0, 255, 0),        # Pure Green
    "YL": (255, 255, 0),      # Pure Yellow
    "SV": (150, 200, 255),    # Light Blue/Silver
    "No": (40, 40, 40)        # Used for non-revenue trains
}

# Typography Colors
AMBER = (255, 176, 0)
WARM_YELLOW = (255, 210, 50)  # Lightbulb yellow for standard text
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 40)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Paths
FONTS_DIR = "/home/brandondiaz/rpi-rgb-led-matrix/fonts"
CUSTOM_FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
