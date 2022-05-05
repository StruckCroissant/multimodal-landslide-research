#!/usr/bin/python3

import sys
import os
from time import sleep, strftime, time
import datetime
import asyncio
import keyboard
import glob
import paho.mqtt.client as mqtt
import json

import libraries
from libraries import *
from concurrent.futures import ThreadPoolExecutor as tex

DEBUG_MODE = False
RPI_OS = libraries.RPi_OS
BACKLOG_SIZE = 20
REF_UNIT = 100
DOUT_PIN = 5
PD_SCK_PIN = 6
CAL_VAL = 2.1745
DEFAULT_LOGFILE = "Strain_Data_Local.csv"
LOG_DIRECTORY_PARENT = "./data/"
TOPIC = "data/strain"
BROKER_ADDR = "192.168.0.130"
connected = False


# Exit Function
def cleanAndExit():
    print("Cleaning.")
    if RPi_OS:
        GPIO.cleanup()
    print("Bye.")
    sys.exit()


# Initialize hx object
def init_sensor():
    hx = HX711(DOUT_PIN, PD_SCK_PIN)
    hx.set_reference_unit(REF_UNIT)
    hx.reset()
    hx.tare()
    keyboard.add_hotkey('0', hx.tare())
    return hx


# Get weight reading from hx object, pair with timestamp
def get_weight(hx):
    data = {
        "val": "{:.2f}".format(hx.get_weight(1) / CAL_VAL),
        "timestamp": str(datetime.datetime.now())
    }
    return data


# Prints data to terminal
def print_data(data):
    print(data['timestamp'])
    print("Current Weight:", data['val'], "g\n")


# Creates data directory
def create_dir():
    try:
        os.mkdir(LOG_DIRECTORY_PARENT)
    except OSError as error:
        print("Data directory exists\n")


# Opens & returns log object
def open_log():
    create_dir()
    filename = DEFAULT_LOGFILE
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    filename = os.path.join(LOG_DIRECTORY_PARENT, filename)
    log = open(filename, "a")
    return log


# Writes data to logfile
def write_data_file(data, log):
    log.write("{:},{:}\n".format(data['timestamp'], float(data['val'])))


# Runs on connecting to topic
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        connected = True
        print("..........")
    else:
        print("Unable To Connect")

    # Automatically subscribes to topic upon reconnect
    client.subscribe(TOPIC)


# Runs main script
def main():
    print("Starting up...")
    hx = init_sensor()
    running = True
    queue = list()
    log = open_log()

    client = mqtt.Client(clean_session=True, client_id="client")
    client.on_connect = on_connect
    print("Connecting to broker...")

    try:
        if not DEBUG_MODE:
            client.connect(BROKER_ADDR)
            client.loop_start()
        else:
            print("Debug mode enabled, disabling MQTT publishing & file writing\n")
            input("Press enter to start data collection...")

    except:
        user_input = input("Failed to connect to broker, continue? (Y/n)")
        user_input.lower().strip()
        if user_input == 'n':
            running = False

    try:
        while (running):
            if len(queue) > BACKLOG_SIZE:
                payload = json.dumps(queue)
                print("Sending Backlog...")
                client.publish(TOPIC, payload)
                queue = []

            data = get_weight(hx)
            queue.append(data)
            print_data(data)
            if not DEBUG_MODE:
                write_data_file(data, log)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
        client.stop_loop()

    log.close()


if __name__ == '__main__':
    main()
