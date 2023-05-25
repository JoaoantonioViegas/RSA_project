import paho.mqtt.client as mqtt
import time
import json
import math as Math
from geopy.distance import distance
from termcolor import colored
from datetime import datetime


class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

post = post(40.636274, -8.647093)
ID = 3
MY_STATUS = "dimmed"
MY_INTENSITY = 20

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/out/lsm")

def on_message(client, userdata, msg):
    global MY_INTENSITY
    msg = json.loads(msg.payload)
    times = msg["dest_stations"]
    dest_stations = list(times.keys())
    dest_stations = [int(i) for i in dest_stations]
    if ID in dest_stations:
        tempo = times[str(ID)]
        print(colored("Tempo: ", "yellow"), colored(tempo, "yellow"))
        MY_INTENSITY = calc_iluminacao(tempo, 3)
        print(colored("Iluminacao: ", "yellow"), colored(MY_INTENSITY, "yellow")) 
        message = construct_message({}, MY_INTENSITY, tempo)
        publish_lsm(message)
    
def construct_message(destination, intensity, tempo):
    f = open('./out_lsm.json')
    m = json.load(f)
    m["dest_stations"] = destination
    m["intensity"] = intensity
    m["station_id"] = ID
    m["station_latitude"] = post.x
    m["station_longitude"] = post.y
    # m["time_to_arrival"] = tempo
    now = datetime.now()
    m["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S:%f")
    m = json.dumps(m)
    return m

def publish_lsm(message):
    client.publish("vanetza/out/lsm", message) #lsm = light support message
    print("LSM published")

def calc_iluminacao(tempo, bias):
    # if(not facing_post):
    #    bias = 2
    luminosidade = 1/tempo*100*bias

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 20
    
    return Math.ceil(luminosidade)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.98.1", 1883, 60)
client.loop_start()

def main():
    print("Starting RSU3")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()

