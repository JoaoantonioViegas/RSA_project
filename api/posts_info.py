import time
import json
from flask import Flask, jsonify
from termcolor import colored
import paho.mqtt.client as mqtt
from flask_cors import CORS

# this program should public the posts information to the "192.168.98.1", 1883, 60 and public the content of the file "posts_coordinaates.json"

broker_address = "192.168.98.1"
broker_port = 1883
topic = "vanetza/posts_info"

client = mqtt.Client()
client.connect(broker_address, broker_port, 60)
client.loop_start()

while True:
    with open('posts_coordinates.json') as json_file:
        data = json.load(json_file)
        client.publish(topic, json.dumps(data))
        print(colored("Published posts information to the MQTT broker", "green"))
    time.sleep(10)
