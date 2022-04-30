#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time

BROKER_ADDR = "192.168.0.130"
TOPIC = "data/strain"
data_array = list()
connected = False
message_recieved = False

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
    contents = str(msg.payload.decode("utf-8")).split(",")
    data = {
        "timestamp" : contents[0],
        "val" : contents[1]
    }

    print(data['timestamp'] + "," +  data['val'])
    #data_array.append(data)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect")

def main():
    client = mqtt.Client("MQTT")

    client.on_message = rec_data
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    
    print("Connecting to broker")
    client.connect(BROKER_ADDR)
    client.loop_start()
    
    print("Subscribing to topic", TOPIC)
    client.subscribe(TOPIC)
    
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        print("Exiting...")

if __name__ == "__main__":
    main()