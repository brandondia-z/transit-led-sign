#!/usr/bin/env python3
"""
Hardware Brightness Stress Test

This script slowly ramps up the brightness of a pure white screen while monitoring
the Raspberry Pi's hardware voltage sensor (vcgencmd). If the power supply drops below
4.63V (brownout risk), it instantly aborts the test and logs the absolute maximum
brightness your power supply can handle.

Usage: sudo ~/wmata_env/bin/python setup/test_max_brightness.py
"""

import time
import sys
import subprocess
import signal
import os

# Add parent directory to path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import StateManager
from src.utils import check_and_stop_service, restart_service
from rgbmatrix import RGBMatrix, RGBMatrixOptions

def check_undervoltage():
    try:
        # Run vcgencmd get_throttled
        result = subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            # output looks like: throttled=0x50005
            if "=" in output:
                hex_val = output.split("=")[1]
                val = int(hex_val, 16)
                # Bit 0 indicates current under-voltage
                is_undervoltage = (val & 1) != 0
                return is_undervoltage
    except Exception as e:
        print(f"Warning: Could not read hardware sensors: {e}")
    return False

def main():
    service_was_stopped = check_and_stop_service()
    
    print("\n" + "="*50)
    print("WARNING: HARDWARE STRESS TEST INITIATED")
    print("="*50)
    print("This will fill the LED matrix with pure white and gradually increase")
    print("brightness until your power supply starts to fail (brownout).")
    print("\nIf your Pi instantly crashes or reboots during this test, your power supply")
    print("safety cutoff is too sensitive. If the test completes successfully, it will")
    print("tell you exactly what your maximum safe brightness limit is.")
    
    resp = input("\nAre you ready to begin? [y/N]: ").strip().lower()
    if resp != 'y':
        print("Aborted.")
        if service_was_stopped:
            restart_service()
        sys.exit(0)

    # Initialize at a safe 10%
    state = StateManager()
    config = state.config
    
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.hardware_mapping = config.gpio_mapping
    options.gpio_slowdown = config.gpio_slowdown
    options.brightness = 10  # Start very low
    options.pwm_bits = 11
    options.drop_privileges = False
    options.led_rgb_sequence = "RBG"
    
    matrix = RGBMatrix(options=options)
    
    def signal_handler(sig, frame):
        matrix.brightness = 10
        matrix.Clear()
        print("\nTest manually aborted.")
        if service_was_stopped:
            restart_service()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\nStarting ramp up... monitoring hardware voltage...")
    matrix.Fill(255, 255, 255)  # Pure White
    
    max_safe = 100
    for b in range(10, 101, 2):  # Go from 10 to 100 in steps of 2
        matrix.brightness = b
        print(f"Testing brightness: {b}%...")
        
        # Hold for 1 second at this brightness to let voltage settle and measure
        start = time.time()
        while time.time() - start < 1.0:
            if check_undervoltage():
                # Instantly drop brightness to save the Pi!
                matrix.brightness = 10
                matrix.Clear()
                print("\n" + "!"*50)
                print(f"CRITICAL: UNDER-VOLTAGE DETECTED AT {b}% BRIGHTNESS!")
                print("!"*50)
                max_safe = b - 5
                print(f"\nYour power supply cannot sustain {b}%.")
                print(f"Your absolute maximum safe limit for pure white is: {max_safe}%")
                if service_was_stopped:
                    restart_service()
                sys.exit(1)
            time.sleep(0.1)
            
    # If we made it here, the power supply is a beast.
    matrix.brightness = 10
    matrix.Clear()
    print("\n" + "="*50)
    print("SUCCESS: Test completed up to 100% brightness!")
    print("="*50)
    print("Your 5V/4A power supply is robust enough to handle the absolute maximum")
    print("load of pure white on this specific matrix.")
    
    if service_was_stopped:
        restart_service()

if __name__ == "__main__":
    main()
