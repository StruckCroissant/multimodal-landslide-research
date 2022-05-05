RPi_OS = True

try:
    global GPIO
    global HX711
    import RPi.GPIO as GPIO
    from libraries.hx711 import HX711
except:
    print("Non-rpi OS detected... \n simulating HX711")
    from libraries.emulated_hx711 import HX711