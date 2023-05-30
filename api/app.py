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

def on_connectStatus(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("all/status")

def on_messageStatus(client, userdata, msg):
    global POSTS_STATUS
    message = json.loads(msg.payload)
    id = str(message['station_id'])
    if id not in POSTS_STATUS:
        POSTS_STATUS[id] = {}

    POSTS_STATUS[id]['ordering_rsu_id'] = message['ordering_rsu_id']
    POSTS_STATUS[id]['in_range'] = message['in_range']



def on_connectPostsAux(client, userdata, flags, rc):
    print("Connected to posts with result code "+str(rc))
    client.subscribe("posts_info")

def on_messagePostsAux(client, userdata, msg):
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
        if 'in_range' not in POSTS_STATUS[key]:
            POSTS_STATUS[key]['in_range'] = False
        if 'ordering_rsu_id' not in POSTS_STATUS[key]:
            POSTS_STATUS[key]['ordering_rsu_id'] = -1

    # print(POSTS_STATUS)

def on_connectLSM(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("all/lsm")

def on_messageLSM(client, userdata, msg):
    global RSU_MESSAGE, POSTS_STATUS
    # print(colored("LSM message", "yellow"))
    message = json.loads(msg.payload)
    # print(message)
    RSU_MESSAGE = msg.payload

    id = str(message["station_id"])
    if id not in POSTS_STATUS:
        POSTS_STATUS[id] = {}
    lat = message["station_latitude"]
    lon = message["station_longitude"]
    intensity = message["intensity"]
    dest_stations = message["dest_stations"]

    if POSTS_STATUS != {}:
        for key, value in dest_stations.items():
            if key not in POSTS_STATUS:
                POSTS_STATUS[str(key)] = {}
            POSTS_STATUS[key]['intensity'] = value
            POSTS_STATUS[key]['ordering_rsu_id'] = int(id)
    

#connect to obu
clientObu = mqtt.Client()
clientObu.on_connect = on_connectObu
clientObu.on_message = on_messageObu
clientObu.connect("192.168.98.20", 1883, 60)

threading.Thread(target=clientObu.loop_forever).start()

#rsus broker
clientStatus = mqtt.Client()
clientStatus.on_connect = on_connectStatus
clientStatus.on_message = on_messageStatus
clientStatus.connect("192.168.98.1", 1883, 60)

threading.Thread(target=clientStatus.loop_forever).start()

#posts broker
clientPostsAux = mqtt.Client()
clientPostsAux.on_connect = on_connectPostsAux
clientPostsAux.on_message = on_messagePostsAux
clientPostsAux.connect("192.168.98.1")

threading.Thread(target=clientPostsAux.loop_forever).start()

#LSM broker
clientLSM = mqtt.Client()
clientLSM.on_connect = on_connectLSM
clientLSM.on_message = on_messageLSM
clientLSM.connect("192.168.98.1")

threading.Thread(target=clientLSM.loop_forever).start()


@app.route('/')
def hello_world():
    return jsonify(message='Hello World!')

@app.route('/api/v1/obu', methods=['GET'])
def get_obu():
    global OBU_MESSAGE
    # print(OBU_MESSAGE)
    return OBU_MESSAGE, 200

@app.route('/api/v1/rsu_data', methods=['GET'])
def get_rsu():
    global POSTS_STATUS
    return POSTS_STATUS, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
