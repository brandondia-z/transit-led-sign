#!/usr/bin/env python3
"""
Hardware Test Script for WMATA LED Sign
Run this on the Pi to verify your hardware mapping and GPIO slowdown settings.

Usage: sudo ~/wmata_env/bin/python setup/test_matrix.py
"""

import time
import argparse
from rgbmatrix import RGBMatrix, RGBMatrixOptions

def test_hardware(mapping, slowdown, brightness):
    print(f"\nTesting: mapping='{mapping}', slowdown={slowdown}, brightness={brightness}%")
    print("Look at the LED panels. They should cycle: RED -> GREEN -> BLUE -> WHITE.")
    print("If the panels are scrambling, glitching, or showing the wrong colors, press Ctrl+C and try a different mapping/slowdown.")
    
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.hardware_mapping = mapping
    options.gpio_slowdown = slowdown
    options.brightness = brightness
    options.pwm_bits = 11
    
    try:
        matrix = RGBMatrix(options=options)
        
        colors = [
            (255, 0, 0, "RED"),
            (0, 255, 0, "GREEN"),
            (0, 0, 255, "BLUE"),
            (255, 255, 255, "WHITE")
        ]
        
        for r, g, b, name in colors:
            print(f"Showing {name}...")
            matrix.Fill(r, g, b)
            time.sleep(2)
            
        print("Success! If the display looked correct, use these settings in your .env file.")
        matrix.Clear()
        
    except Exception as e:
        print(f"Error initializing matrix: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test LED Matrix Hardware")
    parser.add_argument("--mapping", type=str, default="regular", choices=["regular", "adafruit-hat", "adafruit-hat-pwm"], help="Hardware mapping string")
    parser.add_argument("--slowdown", type=int, default=1, choices=[0, 1, 2, 3, 4], help="GPIO slowdown value (1 or 2 recommended for Pi 3B+)")
    parser.add_argument("--brightness", type=int, default=30, help="Brightness percentage (keep low to avoid brownouts on 5V/4A)")
    
    args = parser.parse_args()
    
    print("=== Hardware Validation Test ===")
    print("This test will fill the screen with solid colors.")
    print("If your Pi reboots, your power supply cannot handle the brightness level.")
    print("Press Ctrl+C to cancel if needed.")
    
    time.sleep(2)
    test_hardware(args.mapping, args.slowdown, args.brightness)
