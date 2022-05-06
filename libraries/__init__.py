"""
| Auto-imports RPi libraries on load if they are present & sets RPi_OS variable if not
"""

RPi_OS = True
GPIO = object()
HX711 = object()

try:
    import RPi.GPIO as GPIO
    from libraries.hx711 import HX711
except ImportError:
    print("Non-rpi OS detected... \n simulating HX711")
    from libraries.emulated_hx711 import HX711
    RPi_OS = False
