#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import pandas as pd
import numpy as np
import concurrent.futures.ThreadPoolExecutor() as ex


BROKER_ADDR = "192.168.0.130"
TOPIC = "data/strain"
data_array = list()
connected = False
message_recieved = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        connected = True
        print("..........")
    else:
        print("Unable To Connect")

    client.subscribe(TOPIC)

def rec_data(client, userdata, msg):
    jstring = str(msg.payload.decode("utf-8"))
    dict = JSON.loads(jstring)
    df = pd.DataFrame.from_dict(dict, orient="index")

    print(df)
    #data_array.append(data)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect")

def main():
    print("Starting server...")
    client = mqtt.Client(clean_session=True, client_id="server")

    client.on_message = rec_data
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect


    print("Connecting to broker")
    client.connect(BROKER_ADDR)

    print("Subscribing to topic", TOPIC)
    client.subscribe(TOPIC)


    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        print("Exiting...")

if __name__ == "__main__":
    main()
