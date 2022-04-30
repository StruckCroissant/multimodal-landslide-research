#!/usr/bin/python3

import sys
import os
from time import sleep, strftime, time
import datetime
import asyncio
import keyboard
import glob
import RPi.GPIO as GPIO
from libraries.hx711 import HX711
from signal import pause

REF_UNIT = 100
DOUT_PIN = 5
PD_SCK_PIN = 6
CAL_VAL = 2.1745
LOGFILE = "Strain_Data.csv"
LOG_DIRECTORY_PARENT = "./data/"
TOPIC = "data/strain"

#Exit Function
def cleanAndExit():
    print("Cleaning.")
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

#Get weight reading from hx object, pair with timestamp
def get_weight(hx):
    data = {
        "val" : str(hx.get_weight(1)),
        "timestamp" : str(datetime.datetime.now())
    }
    return data

#Prints data to terminal
def print_data(data):
    print(data['timestamp'])
    print("Current Weight:", data['val'], "g\n")

#Creates data directory
def create_dir():
    try:
        os.mkdir(LOG_DIRECTORY_PARENT)
    except OSError as error:
        print("Data directory exists")

#Opens & returns log object
def open_log():
    create_dir()
    filename = LOGFILE
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    filename = os.path.join(LOG_DIRECTORY_PARENT, filename)
    log = open(filename, "a")
    return log

#Writes data to logfile
def write_data_file(data, log):
    log.write("{0},{1}\n".format(data['timestamp'], data['val']))

#Returns the average of all data points in the list.
def getAverage(arr):
    return (sum(arr[len(arr) - 5:len(arr) - 1])/5) + 2

#Runs main script
def main():
    hx = init_sensor()
    keyboard.add_hotkey('0', hx.tare())
    running = True
    slowmode = False #determines if slow mode is currently on
    subset = 0 #tracks the amount of subsets processed
    arr = []
    log = open_log()

    try:
        while (running):
            data = get_weight(hx)
            arr.append(data['val'])
            print_data(data)
            write_data_file(data, log)

            # UNUSED CODE
            # Determines recording frequency on weight increase
            '''
            movingaverage = getAverage(arr)
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
                running = False

    except (KeyboardInterrupt, SystemExit):
            cleanAndExit()

if __name__ == '__main__':
    main()
