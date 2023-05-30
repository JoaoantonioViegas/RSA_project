#Create a simple Flask app that returns a JSON object with a key of 'message' and value of 'Hello World!'.
import time
import json
from flask import Flask, jsonify
from termcolor import colored
import paho.mqtt.client as mqtt
import threading
from flask_cors import CORS

OBU_MESSAGE = None
rsu_MESSAGE = None
POSTS_status = {}

ORDERING_INTENSITIES = {}

OBUS = {}

app = Flask(__name__)
CORS(app)

#connect to cams
def on_connectObu1(client, userdata, flags, rc):
    print("Connected to cams with result code "+str(rc))
    client.subscribe("vanetza/out/cam")

def on_messageObu1(client, userdata, msg):
    global OBU_MESSAGE, OBUS
    # print(colored("CAM message", "green"))
    message = json.loads(msg.payload)
    OBU_MESSAGE = msg.payload
    longitude = message["longitude"]
    latitude = message["latitude"]
    speed = message["speed"]
    obu_id = message["stationID"]

    if(obu_id not in OBUS):
        OBUS[obu_id] = {"longitude": longitude, "latitude": latitude, "speed": speed}
        return
    else:
        OBUS[obu_id]["longitude"] = longitude
        OBUS[obu_id]["latitude"] = latitude
        OBUS[obu_id]["speed"] = speed

def on_connectstatus(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("all/status")

def on_messagestatus(client, userdata, msg):
    global POSTS_status
    message = json.loads(msg.payload)
    id = str(message['station_id'])
    if id not in POSTS_status:
        POSTS_status[id] = {}

    POSTS_status[id]['ordering_rsu_id'] = message['ordering_rsu_id']
    POSTS_status[id]['in_range'] = message['in_range']



def on_connectPostsAux(client, userdata, flags, rc):
    print("Connected to posts with result code "+str(rc))
    client.subscribe("posts_info")

def on_messagePostsAux(client, userdata, msg):
    global POSTS_status, ORDERING_INTENSITIES
    message = json.loads(msg.payload)
    for key, value in message.items():
        if key not in POSTS_status:
            POSTS_status[key] = {}
        if key not in ORDERING_INTENSITIES:
            ORDERING_INTENSITIES[key] = {}

        POSTS_status[key]['lat'] = value['latitude']
        POSTS_status[key]['lon'] = value['longitude']
        POSTS_status[key]['status'] = value['status']
        POSTS_status[key]['rsu'] = value['rsu']
        #check if POSTS_status has intensity
        if 'intensity' not in POSTS_status[key]:
            POSTS_status[key]['intensity'] = 20 
        if 'in_range' not in POSTS_status[key]:
            POSTS_status[key]['in_range'] = False
        if 'ordering_rsu_id' not in POSTS_status[key]:
            POSTS_status[key]['ordering_rsu_id'] = -1
        if 'close_stations' not in POSTS_status[key]:
            POSTS_status[key]['close_stations'] = []

    # print(POSTS_status)

def on_connectLSM(client, userdata, flags, rc):
    print("Connected to rsus with result code "+str(rc))
    client.subscribe("all/lsm")

def on_messageLSM(client, userdata, msg):
    global rsu_MESSAGE, POSTS_status, ORDERING_INTENSITIES
    message = json.loads(msg.payload)
    # print(message)
    rsu_MESSAGE = msg.payload

    id = str(message["station_id"])
    if id not in POSTS_status:
        POSTS_status[id] = {}
    lat = message["station_latitude"]
    lon = message["station_longitude"]
    intensity = message["intensity"]
    dest_stations = message["dest_stations"]
    POSTS_status[id]['intensity'] = intensity
    POSTS_status[id]['close_stations'] = list(dest_stations.keys())

    # for key, value in POSTS_status.items():
    #     if 'close_stations' not in POSTS_status[key]:
    #         POSTS_status[key]['close_stations'] = []
    #     close_stations = dest_stations.keys()
    #     POSTS_status[key]['close_stations'] = close_stations 

    # print(dest_stations)

    #for each post, adds the intensity that it receives from the rsu (id)

    # for key, value in ORDERING_INTENSITIES.items():
    #     ORDERING_INTENSITIES[key][id] = dest_stations[key]
    
    # #for each post, gets the intensity by averaging the intensities received from each rsu

    # if POSTS_status != {}:
    #     for key, value in ORDERING_INTENSITIES.items():
    #         if key not in POSTS_status:
    #             POSTS_status[str(key)] = {}
    #         average = 0
    #         for k, v in value.items():
    #             if v != -1:
    #                 average += v
    #         average = average/len(value)
    #         POSTS_status[key]['intensity'] = average
    #         POSTS_status[key]['ordering_rsu_id'] = int(id)

    # print("-------------------")
    # print(message)
    # print(ORDERING_INTENSITIES)

    if POSTS_status != {}:
        for key, value in dest_stations.items():
            if key not in POSTS_status:
                POSTS_status[str(key)] = {}
            POSTS_status[key]['intensity'] = value
            POSTS_status[key]['ordering_rsu_id'] = int(id)
    

#connect to obu
clientObu1 = mqtt.Client()
clientObu1.on_connect = on_connectObu1
clientObu1.on_message = on_messageObu1
clientObu1.connect("192.168.98.10", 1883, 60)

threading.Thread(target=clientObu1.loop_forever).start()

#rsus broker
clientstatus = mqtt.Client()
clientstatus.on_connect = on_connectstatus
clientstatus.on_message = on_messagestatus
clientstatus.connect("192.168.98.1", 1883, 60)

threading.Thread(target=clientstatus.loop_forever).start()

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
    global OBUS
    # print(OBUS)
    return OBUS, 200

@app.route('/api/v1/rsu_data', methods=['GET'])
def get_rsu():
    global POSTS_status
    return POSTS_status, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
