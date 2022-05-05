'''
Auto-imports RPi libraries on load if they are present & sets RPi_OS variable if not
'''

RPi_OS = True
try:
    global GPIO
    global HX711
    import RPi.GPIO as GPIO
    from libraries.hx711 import HX711
except:
    print("Non-rpi OS detected... \n simulating HX711")
    from libraries.emulated_hx711 import HX711
    RPi_OS = False