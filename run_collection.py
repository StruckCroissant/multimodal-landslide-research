#!/usr/bin/python3

from time import sleep, strftime, time
import sys
import datetime
import asyncio
import keyboard
import glob
from signal import pause

REF_UNIT = 100
DOUT_PIN = 5
PD_SCK_PIN = 6
CAL_VAL = 2.1745
LOGFILE = "Strain_Data.csv"
LOG_DIRECTORY = "/data/"

#Set up HX711 Driver
sys.path.insert(0, '/libraries')
EMULATE_HX711=False
if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

#Exit Function
def cleanAndExit():
    print("Cleaning.")
    if not EMULATE_HX711:
        GPIO.cleanup()
    print("Bye.")
    sys.exit()

#Initialize hx object
def init_sensor():
    hx = HX711(DOUT_PIN, PD_SCK_PIN)
    hx.set_reference_unit(REF_UNIT)
    hx.reset()
    hx.tare()
    return hx

#Get weight reading from hx object
def get_weight(hx):
    return hx.get_weight(1) / CAL_VAL

#Prints data to terminal
def print_data(val):
    print(str(datetime.datetime.now()))
    print("Current Weight:", val, "g\n")

#Opens & returns log object
def open_log():
    filename = LOGFILE
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    filename = LOG_DIRECTORY + filename
    log = open(filename, "a")
    return log

#Writes data to logfile
def write_data_file(Data, log):
    log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(Data)))
    log.write("{0},{1}\n".format(str(datetime.datetime.now()),str(Data)))

#Returns the average of all data points in the list.
def getAverage(arr):
    return (sum(arr[len(arr) - 5:len(arr) - 1])/5) + 2

movingaverage = 1 #This is holds the moving average that will be used to determine recording frequency

hx = init_sensor()
keyboard.add_hotkey('0', hx.tare())
go = True
slowmode = False #determines if slow mode is currently on
subset = 0 #tracks the amount of subsets processed
arr = []
log = open_log()


try:
    while (go):
        val = get_weight(hx)
        valtime = datetime.datetime.now() #timestamp
        arr.append(val)
        print_data(val)
        write_data_file(val, log)
        movingaverage = getAverage(arr)


        # UNUSED CODE
        # Determines recording frequency on weight increase
        '''
        if(val < movingaverage):
            sleep(0.4122) #slow mode, time.sleep makes rate two points/second
            if(slowmode == False): #lets user know when slow mode is activated
                slowmode = True
                print("Slow Mode ON")
        else:
            if(slowmode == True):
                slowmode = False
                print("Slow Mode is OFF")

        if(len(arr) % 5 == 0): #once we have a new subset of 5, calculate average
            subset = subset + 1
            movingaverage = getAverage() #function calculates average
            print("Current Moving Average:" + str(getAverage()))
            print("Subset:" + str(subset)) #current subset
            print("Array Length:" + str(len(arr))) #shows subsets are being calculated correctly
            # Do moving average calculations
            # Get a value for the average
        '''

        if keyboard.is_pressed('alt'):
            go = False

except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
