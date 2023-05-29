#Create a simple Flask app that returns a JSON object with a key of 'message' and value of 'Hello World!'.
import time
import json
from flask import Flask, jsonify
from termcolor import colored
import paho.mqtt.client as mqtt
import threading
from flask_cors import CORS

OBU_MESSAGE = None
RSU_MESSAGE = None
POSTS_STATUS = {}

app = Flask(__name__)
CORS(app)

#connect to cams
def on_connectObu(client, userdata, flags, rc):
    print("Connected to cams with result code "+str(rc))
    client.subscribe("vanetza/out/cam")

def on_messageObu(client, userdata, msg):
    global OBU_MESSAGE
    # print(colored("CAM message", "green"))
    message = json.loads(msg.payload)
    # print(message)
    OBU_MESSAGE = msg.payload

def on_connect(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("all/lsm")

def on_connectPosts(client, userdata, flags, rc):
    print("Connected to posts with result code "+str(rc))
    client.subscribe("posts_info")

def on_messagePosts(client, userdata, msg):
    global POSTS_STATUS
    message = json.loads(msg.payload)
    for key, value in message.items():
        if key not in POSTS_STATUS:
            POSTS_STATUS[key] = {}

        POSTS_STATUS[key]['lat'] = value['Latitude']
        POSTS_STATUS[key]['lon'] = value['Longitude']
        POSTS_STATUS[key]['status'] = value['Status']
        POSTS_STATUS[key]['rsu'] = value['RSU']
        #check if POSTS_STATUS has intensity
        if 'intensity' not in POSTS_STATUS[key]:
            POSTS_STATUS[key]['intensity'] = 20 


def on_message(client, userdata, msg):
    global RSU_MESSAGE, POSTS_STATUS
    # print(colored("LSM message", "yellow"))
    message = json.loads(msg.payload)
    # print(message)
    RSU_MESSAGE = msg.payload

    id = message["station_id"]
    lat = message["station_latitude"]
    lon = message["station_longitude"]
    intensity = message["intensity"]
    dest_stations = message["dest_stations"]

    # print(POSTS_STATUS)
    if POSTS_STATUS != {}:
        for key, value in dest_stations.items():
            POSTS_STATUS[key]['intensity'] = value
    

#connect to obu
clientObu = mqtt.Client()
clientObu.on_connect = on_connectObu
clientObu.on_message = on_messageObu
clientObu.connect("192.168.98.20", 1883, 60)

threading.Thread(target=clientObu.loop_forever).start()

#rsus broker
clientLocal = mqtt.Client()
clientLocal.on_connect = on_connect
clientLocal.on_message = on_message
clientLocal.connect("192.168.98.1", 1883, 60)

threading.Thread(target=clientLocal.loop_forever).start()

#posts broker
clientPosts = mqtt.Client()
clientPosts.on_connect = on_connectPosts
clientPosts.on_message = on_messagePosts
clientPosts.connect("192.168.98.1")

threading.Thread(target=clientPosts.loop_forever).start()


@app.route('/')
def hello_world():
    return jsonify(message='Hello World!')

@app.route('/api/v1/obu', methods=['GET'])
def get_obu():
    global OBU_MESSAGE
    return OBU_MESSAGE, 200

@app.route('/api/v1/rsu_data', methods=['GET'])
def get_rsu():
    global POSTS_STATUS
    return POSTS_STATUS, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
