#!/usr/bin/python3
from datetime import datetime as dt
import os
import sys
from socket import socket

import paho.mqtt.client as mqtt
import time
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor as tex
import json
import matplotlib.pyplot as plt

# Initializing global variables
BROKER_ADDR = str()
TOPIC = str()
LOG_DIRECTORY_PARENT = str()
LOGFILE = str()

# Local settings
DEBUG_MODE = False
strain_df = pd.DataFrame(columns=['timestamp', 'val'])
connected = False
message_recieved = False


# Creates data directory
def create_dir():
    try:
        os.mkdir(LOG_DIRECTORY_PARENT)
    except OSError as error:
        print("Data directory exists")


# Opens & returns log object
def open_log():
    create_dir()
    filename = LOGFILE
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    filename = os.path.join(LOG_DIRECTORY_PARENT, filename)
    log = open(filename, "a")
    return log


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        global connected
        connected = True
        print("..........")
    else:
        print("Unable To Connect")

    client.subscribe(TOPIC)


def rec_data(client, userdata, msg):
    jstring = str(msg.payload.decode("utf-8"))
    df = pd.DataFrame(json.loads(jstring))
    df = df.set_index('timestamp')

    global strain_df
    strain_df = pd.concat([strain_df, df])

    print(strain_df)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect")


def _load_settings() -> None:
    try:
        fh = open("settings.json")
        js_settings = json.load(fh)
    except FileNotFoundError:
        opt = "n"
        opt = input("Settings file not found; continue? (y/N)").strip().lower()
        if opt == "n":
            sys.exit()

    server_settings = js_settings['server']
    master_settings = js_settings['master']

    global BROKER_ADDR
    global TOPIC
    global LOG_DIRECTORY_PARENT
    global LOGFILE
    BROKER_ADDR = master_settings['broker_address']
    TOPIC = master_settings['strain_topic']
    LOG_DIRECTORY_PARENT = master_settings['log_directory_parent']
    today = dt.now()
    LOGFILE = server_settings['default_logfile'] + \
        "_{:02d}{:02d}{:}".format(today.day, today.month, today.year)


def _init():
    print("Initializing...")
    global strain_df
    strain_df = strain_df.set_index('timestamp')


def main():
    print("Starting server...")
    client = mqtt.Client(clean_session=True, client_id="server")

    client.on_message = rec_data
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        print("Connecting to broker")
        client.connect(BROKER_ADDR)
    except OSError:
        print("Broker Connection failed. Exiting...")
        sys.exit()

    print("Subscribing to topic", TOPIC)
    client.subscribe(TOPIC)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        print("Exiting...")


if __name__ == "__main__":
    _init()
    _load_settings()
    main()
