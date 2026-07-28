import os
import sys

def hex_to_bits(hex_str, width):
    num_bits = len(hex_str) * 4
    bin_str = bin(int(hex_str, 16))[2:].zfill(num_bits)
    return bin_str[:width]

class TerminalFont:
    def __init__(self, path):
        self.chars = {}
        with open(path, 'r') as f:
            lines = f.readlines()
            
        in_char = False
        current_char = ""
        bitmap_lines = []
        width = 0
        height = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("ENCODING"):
                try:
                    code = int(line.split()[1])
                    if code >= 0 and code < 0x110000:
                        in_char = True
                        current_char = chr(code)
                        bitmap_lines = []
                except ValueError:
                    pass
            elif line.startswith("BBX"):
                parts = line.split()
                if in_char:
                    width = int(parts[1])
                    height = int(parts[2])
            elif in_char and line == "BITMAP":
                j = i + 1
                while j < len(lines) and not lines[j].startswith("ENDCHAR"):
                    bitmap_lines.append(lines[j].strip())
                    j += 1
                
                char_bits = []
                for hex_str in bitmap_lines:
                    char_bits.append(hex_to_bits(hex_str, width))
                self.chars[current_char] = char_bits
                in_char = False

class TerminalRenderer:
    def __init__(self):
        self.width = 128
        self.height = 32
        self.canvas = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        
        font_path = os.path.join(os.path.dirname(__file__), "src", "fonts", "wmata_5x7.bdf")
        self.font_wmata_5x7 = TerminalFont(font_path)

    def clear(self):
        self.canvas = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]

    def draw_text(self, font, x, y, color_name, text):
        colors = {
            "RED": (255, 0, 0),
            "AMBER": (255, 176, 0),
            "WHITE": (255, 255, 255),
            "LINE_RD": (229, 22, 54),
            "LINE_BL": (21, 116, 196),
            "LINE_OR": (246, 135, 18),
            "LINE_GR": (15, 171, 75),
            "LINE_YL": (252, 208, 6),
            "LINE_SV": (162, 170, 173)
        }
        color = colors.get(color_name, (255, 255, 255))
        
        # BDF baseline is y. The characters are 7 pixels high (y-6 to y)
        curr_x = x
        for char in text:
            if char in font.chars:
                bits = font.chars[char]
                char_h = len(bits)
                char_w = len(bits[0]) if char_h > 0 else 0
                
                # Draw character
                for row_idx, row_bits in enumerate(bits):
                    draw_y = y - char_h + 1 + row_idx
                    for col_idx, bit in enumerate(row_bits):
                        draw_x = curr_x + col_idx
                        if bit == '1' and 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                            self.canvas[draw_y][draw_x] = color
                curr_x += char_w + 1 # +1 for character spacing
            else:
                curr_x += 6 # Unknown character, jump 6 pixels
        return curr_x - x

    def render_to_terminal(self):
        print("\n+" + "-" * self.width + "+")
        for row in self.canvas:
            sys.stdout.write("|")
            for r, g, b in row:
                if r == 0 and g == 0 and b == 0:
                    sys.stdout.write(" ")
                else:
                    # ANSI truecolor background block
                    sys.stdout.write(f"\033[38;2;{r};{g};{b}m█\033[0m")
            sys.stdout.write("|\n")
        print("+" + "-" * self.width + "+\n")


if __name__ == "__main__":
    from src.display_modes import compact
    from src.models import TrainPrediction
    
    renderer = TerminalRenderer()
    
    # Mock state
    mock_state = {
        "api_error": False,
        "predictions": [
            TrainPrediction("OR", "N Carrollton", "New Carrollton", "BRD", "6", "1", "A01"),
            TrainPrediction("BL", "Largo", "Largo Town Center", "3", "6", "1", "A01"),
            TrainPrediction("SV", "N Carrollton", "New Carrollton", "7", "8", "1", "A01")
        ]
    }
    
    compact.render(renderer, mock_state)
    renderer.render_to_terminal()
