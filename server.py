#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time

BROKER_ADDR = ""
TOPIC = "data/strain"
data_array = list()
connected = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        connected = True
        print("Connected")
        print("..........")
    else:
        print("Unable To Connect")

    client.subscribe(TOPIC)

def rec_data(client, userdata, msg):
    contents = msg.payload.split(",")
    data = {
        "timestamp" : contents[0],
        "val" : contents[1]
    }

    print(data['timestamp', ], ",", data['val'])
    data_array.append(data)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect")

def main():
    client = mqtt.Client("MQTT")

    client.on_message = rec_data
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.loop_start()
    client.subscribe(TOPIC)


if "__name__" == "__main__":
    main()
