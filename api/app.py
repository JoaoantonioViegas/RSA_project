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
RSUS_STATUS = {}

app = Flask(__name__)
CORS(app)

#connect to cams
def on_connectObu(client, userdata, flags, rc):
    print("Connected to cams with result code "+str(rc))
    client.subscribe("vanetza/in/cam")

def on_messageObu(client, userdata, msg):
    global OBU_MESSAGE
    # print(colored("CAM message", "green"))
    message = json.loads(msg.payload)
    # print(message)
    OBU_MESSAGE = msg.payload

def on_connect(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("vanetza/out/lsm")

def on_message(client, userdata, msg):
    global RSU_MESSAGE, RSUS_STATUS
    # print(colored("LSM message", "yellow"))
    message = json.loads(msg.payload)
    # print(message)
    RSU_MESSAGE = msg.payload

    id = message["station_id"]
    lat = message["station_latitude"]
    lon = message["station_longitude"]
    intensity = message["intensity"]

    #check if rsu is already in the dictionary
    if id in RSUS_STATUS:
        #update rsu status
        RSUS_STATUS[id]["intensity"] = intensity
        RSUS_STATUS[id]["lat"] = lat
        RSUS_STATUS[id]["lon"] = lon
    else:
        #add new rsu
        RSUS_STATUS[id] = {
            "intensity": intensity,
            "lat": lat,
            "lon": lon,
        }

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


@app.route('/')
def hello_world():
    return jsonify(message='Hello World!')

@app.route('/api/v1/obu', methods=['GET'])
def get_obu():
    global OBU_MESSAGE
    return OBU_MESSAGE, 200

@app.route('/api/v1/rsu_data', methods=['GET'])
def get_rsu():
    global RSUS_STATUS
    return RSUS_STATUS, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
