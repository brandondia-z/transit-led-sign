import os
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
except ImportError:
    # Dummy classes for local Mac testing where library isn't available
    class RGBMatrixOptions: pass
    class RGBMatrix: pass
    class graphics:
        class Color:
            def __init__(self, r, g, b): pass
        class Font:
            def __init__(self): self.height = 0
            def LoadFont(self, path): pass

from src.constants import FONTS_DIR, CUSTOM_FONTS_DIR, LINE_COLORS, AMBER, WARM_YELLOW, WHITE, DARK_GRAY, BLACK, RED, GREEN, CYAN, MAGENTA

class Renderer:
    def __init__(self, config):
        options = RGBMatrixOptions()
        
        # Only set these if we successfully imported the real library
        if hasattr(options, 'rows'):
            options.rows = 32
            options.cols = 64
            options.chain_length = 2
            options.parallel = 1
            options.hardware_mapping = config.gpio_mapping
            options.gpio_slowdown = config.gpio_slowdown
            options.brightness = config.brightness
            options.pwm_bits = 11
            options.drop_privileges = False
            options.led_rgb_sequence = "RBG" # Fix for panels where Blue and Green are swapped!
            
            self.matrix = RGBMatrix(options=options)
            self.canvas = self.matrix.CreateFrameCanvas()
        else:
            self.matrix = None
            self.canvas = None
            print("WARNING: rgbmatrix not found. Running in mock mode.")

        # Load Fonts
        self.font_wmata_5x7 = self._load_custom_font("wmata_5x7.bdf")
        self.font_5x7 = self._load_font("5x7.bdf")
        self.font_5x8 = self._load_font("5x8.bdf")
        self.font_6x10 = self._load_font("6x10.bdf")
        self.font_4x6 = self._load_font("4x6.bdf")

        # Create Color Objects
        self.colors = {
            "AMBER": self._make_color(*AMBER),
            "WARM_YELLOW": self._make_color(*WARM_YELLOW),
            "WHITE": self._make_color(*WHITE),
            "DARK_GRAY": self._make_color(*DARK_GRAY),
            "BLACK": self._make_color(*BLACK),
            "RED": self._make_color(*RED),
            "GREEN": self._make_color(*GREEN),
            "CYAN": self._make_color(*CYAN),
            "MAGENTA": self._make_color(*MAGENTA)
        }
        
        for line, rgb in LINE_COLORS.items():
            self.colors[f"LINE_{line}"] = self._make_color(*rgb)

    def _load_font(self, filename):
        f = graphics.Font()
        path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(path):
            f.LoadFont(path)
        return f

    def _load_custom_font(self, filename):
        f = graphics.Font()
        path = os.path.join(CUSTOM_FONTS_DIR, filename)
        if os.path.exists(path):
            f.LoadFont(path)
        return f

    def _make_color(self, r, g, b):
        return graphics.Color(r, g, b)

    def clear(self):
        if self.canvas:
            self.canvas.Clear()

    def swap(self):
        if self.matrix and self.canvas:
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def draw_text(self, font, x, y, color_key, text):
        if not self.canvas:
            return len(text) * 6 # mock width
        c = self.colors.get(color_key, self.colors["WHITE"])
        return graphics.DrawText(self.canvas, font, x, y, c, text)

    def draw_line(self, x1, y1, x2, y2, color_key):
        if not self.canvas:
            return
        c = self.colors.get(color_key, self.colors["WHITE"])
        graphics.DrawLine(self.canvas, x1, y1, x2, y2, c)
        
    def draw_rect(self, x, y, w, h, color_key):
        if not self.canvas:
            return
        c = self.colors.get(color_key, self.colors["WHITE"])
        # Simple filled rect using DrawLine
        for i in range(h):
            graphics.DrawLine(self.canvas, x, y+i, x+w-1, y+i, c)
            
    def set_pixel(self, x, y, r, g, b):
        if not self.canvas:
            return
        self.canvas.SetPixel(x, y, r, g, b)
