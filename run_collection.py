"""
| Runs data collection on HX711 sensor, writes to file, and publishes to MQTT topic automatically
"""

#!/usr/bin/python3

import sys
import os
import datetime
import keyboard
import paho.mqtt.client as mqtt
import json

import libraries
from libraries import HX711, GPIO

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


def clean_and_exit() -> None:
    """
    | Cleans GPIO if it on Raspbian
    :return: none
    """
    print("Cleaning.")
    if libraries.RPi_OS:
        GPIO.cleanup()
    print("Bye.")
    sys.exit()


def init_sensor() -> HX711:
    """
    | Initializes HX711 sensor object
    :return: HX711 Object
    """
    hx = HX711(DOUT_PIN, PD_SCK_PIN)
    hx.set_reference_unit(REF_UNIT)
    hx.reset()
    hx.tare()
    keyboard.add_hotkey('0', hx.tare())
    return hx


def get_weight(hx: HX711) -> dict:
    """
    | Takes HX711 object & returns a dictionary with a weight reading and timestamp
    :param hx: HX711 object
    :return: dict
    """
    data = {
        "val": "{:.2f}".format(hx.get_weight(1) / CAL_VAL),
        "timestamp": str(datetime.datetime.now())
    }
    return data


def print_data(data: dict) -> None:
    """
    | Takes a data dict and prints data to stdout
    :param data: hx data dict
    :return: None
    """
    print(data['timestamp'])
    print("Current Weight:", data['val'], "g\n")


def create_dir() -> None:
    """
    | Creates log directory if it doesn't exist
    :return: None
    """
    try:
        os.mkdir(LOG_DIRECTORY_PARENT)
    except OSError:
        print("Data directory exists\n")


def open_log() -> open:
    """
    | Creates log object with selected path
    :return: open object
    """
    create_dir()
    filename = DEFAULT_LOGFILE
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    filename = os.path.join(LOG_DIRECTORY_PARENT, filename)
    log = open(filename, "a")
    return log


def write_data_file(data: dict, log: open) -> None:
    """
    | Writes data dict to file
    :param data: dict
    :param log: open object
    :return: None
    """
    log.write("{:},{:}\n".format(data['timestamp'], float(data['val'])))


def on_connect(client: mqtt.Client, userdata: object, flags: object, rc: object) -> None:
    """
    | Specifies actions on connection to topic
    :param client: mqtt.Client
    :param userdata: object
    :param flags: object
    :param rc: object
    :return: None
    """
    if rc == 0:
        print("Connected")
        global connected
        connected = True
        print("..........")
    else:
        print("Unable To Connect")

    # Automatically subscribes to topic upon reconnect
    client.subscribe(TOPIC)


def main() -> None:
    """
    | Runs main data collection script
    :return: None
    """
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
        user_input = input("Failed to connect to broker, continue? (Y/n)").lower().strip()
        if user_input == 'n':
            running = False
    finally:
        try:
            # Main data collection loop
            while running:
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
            clean_and_exit()
            client.stop_loop()

    log.close()


if __name__ == '__main__':
    main()
