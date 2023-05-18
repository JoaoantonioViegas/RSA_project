import paho.mqtt.client as mqtt
import time
import json
import random
from geopy.distance import distance
from termcolor import colored


class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

post = post(40.635986, -8.646732)
pair_post = post(40.636028, -8.646669)
post3 = post(40.635995, -8.646634)
post4 = post(40.635953, -8.646696)

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
    print("Starting RSU2")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()

