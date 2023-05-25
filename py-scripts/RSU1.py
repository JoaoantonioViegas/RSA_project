import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import random
from geopy.distance import distance
from termcolor import colored
import math as Math
import threading

class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

ID = 1
post = post(40.636032, -8.646632)

LAMPS = {
    1: [40.636032, -8.646632],
    2: [40.635674, -8.646346],
    3: [40.636274, -8.647093],
}

turn_light_on_message = {
    "my_status": "on",
    "ordering_status": "on",
    "longitude": post.y,
    "latitude": post.x,
    "stationID": 1,
}
turn_light_on_message = json.dumps(turn_light_on_message)


syncronize_message = {
   "status":"on",
   "percentage":20,
   "longitude":post.y,
   "latitude":post.x,
   "stationID":35,
   "ordering_status":"on",
   "ordering_percentage":20,
   "ordering_interval":4000,
   "radius":30,
   "timestamp":"yyyymmddhhmmss",
   "sequence_number":10,
}
syncronize_message = json.dumps(syncronize_message)

MY_STATUS = "dimmed"
MY_INTENSITY = 20
RADIUS = 100

last_3_distances = []

#mosquitto_sub -h 192.168.98.1 -t "vanetza/in/cam" -v 
def on_connectObu(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/in/cam")

def on_connectRsu(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/out/lsm")


def on_messageRsu(client, userdata, msg):
    message = json.loads(msg.payload)
    # print(msg.topic+" "+str(msg.payload))

def on_messageObu(client, userdata, msg):
    global MY_STATUS, MY_INTENSITY

    # print(msg.topic+" "+str(msg.payload))

    message = json.loads(msg.payload)
    # check the message parameters "longitude"
    longitude = message["longitude"]

    latitude = message["latitude"]

    velocity = message["speed"]

    distance_between_car_and_post = round(distance((latitude, longitude), (post.x, post.y)).meters,2)

    last_3_distances.append(distance_between_car_and_post)
    if len(last_3_distances) > 3:
        last_3_distances.pop(0)

    facing = facing_post(last_3_distances)

    print(colored("Distance between car and post: ","blue"), distance_between_car_and_post)
    print(colored("Not facing post: ", "blue"), facing)
    print(colored("Speed: ", "blue"), velocity)

    if(MY_STATUS == "on"):
        print(colored("My status: ", "green"), colored(MY_STATUS, "green"))
    else:
        print(colored("My status: ", "red"), colored(MY_STATUS, "red"))

    time_to_arrival = [round(calc_interval(distance_between_car_and_post, velocity),2)]
    print(colored("Time to arrival: ", "green"), time_to_arrival)
    # if(not facing):
    #     time_to_arrival = 0
    iluminacao = calc_iluminacao(distance_between_car_and_post,velocity, 3, facing)
    MY_INTENSITY = iluminacao

    if iluminacao > 20 and MY_STATUS == "dimmed":
        MY_STATUS = "on"
    
    elif iluminacao <= 20 and MY_STATUS == "on":
        MY_STATUS = "dimmed"

    print(colored("Iluminacao: ", "yellow"), colored(iluminacao, "yellow"))  
    print("\n")

    target_ids = get_post_ids()
    times = get_times_to_arrival(target_ids, latitude, longitude, velocity)
    out_message = construct_message([2], MY_INTENSITY, times)
    publish_lsm(out_message)
    
def publish_lsm(message):
    clientRsu.publish("vanetza/out/lsm", message) #lsm = light support message
    print(message)
    print("LSM published")


def calc_iluminacao(distance, speed, bias, facing_post):
    tempo = calc_interval(distance, speed)
    # if(not facing_post):
    #    bias = 2
    luminosidade = 1/tempo*100*bias

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 20

    if distance < 20:
        return 100
    
    return Math.ceil(luminosidade)

def calc_interval(distance, speed):
    # Converter a speed para metros por segundo
    speed_ms = speed * (1000/3600)

    # Calcular o tempo em segundos
    tempo = distance / speed_ms
    return tempo

def facing_post(last_3_distances):
    if len(last_3_distances) == 3:
        if last_3_distances[0] > last_3_distances[1] and last_3_distances[1] > last_3_distances[2]:
            return True
    return False

def construct_message(destination, intensity, times):
    f = open('./out_lsm.json')
    m = json.load(f)
    m["dest_stations"] = times
    m["intensity"] = intensity
    m["station_id"] = ID
    m["station_latitude"] = post.x
    m["station_longitude"] = post.y
    # m["time_to_arrival"] = time_to_arrival
    now = datetime.now()
    m["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S:%f")
    m = json.dumps(m)
    return m

def get_post_ids():
    global LAMPS
    ids = []
    for key, value in LAMPS.items():
        # if(post.x != value[0] and post.y != value[1]):
            #check if lamp is within radius
        if distance((post.x, post.y), (value[0], value[1])).meters < RADIUS:
            ids.append(key)
    return ids

def get_times_to_arrival(ids, car_latitude, car_longitude, car_speed):
    global LAMPS
    times = {}
    for id in ids:
        distance_between_car_and_post = round(distance((car_latitude, car_longitude), (LAMPS[id][0], LAMPS[id][1])).meters,2)
        time_to_arrival = round(calc_interval(distance_between_car_and_post, car_speed),2)
        times[id] = time_to_arrival
    return times


clientObu = mqtt.Client()
clientObu.on_connect = on_connectObu
clientObu.on_message = on_messageObu
clientObu.connect("192.168.98.20", 1883, 60)
threading.Thread(target=clientObu.loop_forever).start()

clientRsu = mqtt.Client()
clientRsu.on_connect = on_connectRsu
clientRsu.on_message = on_messageRsu
clientRsu.connect("192.168.98.1", 1883, 60)
threading.Thread(target=clientRsu.loop_forever).start()


def main():
    print("Starting RSU1")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()