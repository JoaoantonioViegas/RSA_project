import paho.mqtt.client as mqtt
import time
import json
import random
from termcolor import colored


class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y


post = post(40.63605, -8.64657)

turn_light_on_message = {
    "my_status": "on",
    "ordering_status": "on",
    "longitude": post.y,
    "latitude": post.x,
    "stationID": 2,
}

# wait to consume data from the broker vanetza/out/lsm
# 

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/out/lsm")

def on_message(client, userdata, msg):
    msg = json.loads(msg.payload)
    print(msg)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.98.20", 1883, 60)
client.loop_start()

def main():
    print("Starting RSU3")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()



