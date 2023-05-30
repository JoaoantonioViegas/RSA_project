import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import sys
from geopy.distance import distance
from termcolor import colored
import math as Math
import threading

class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# ID = 11
# post = post(40.636991, -8.647816)
# BIAS = 2.8   


#make sure the program is called with the correct number of arguments (6)
if len(sys.argv) != 6:
    print("Usage: python3 RSU.py <ID> <latitude> <longitude> <bias> <IP>")
    sys.exit(1)

#assign the arguments to variables
ID = int(sys.argv[1])
print(colored("ID: ", "magenta"), colored(ID, "magenta"))
post.x = float(sys.argv[2])
print(colored("post.x: ", "magenta"), colored(post.x, "magenta"))
post.y = -float(sys.argv[3])
print(colored("post.y: ", "magenta"), colored(post.y, "magenta"))
BIAS = float(sys.argv[4])
print(colored("BIAS: ", "magenta"), colored(BIAS, "magenta"))
IP = sys.argv[5]
print(colored("IP: ", "magenta"), colored(IP, "magenta"))
post = post(post.x, post.y)
LAMPS = {}

MY_STATUS = "dimmed"
MY_INTENSITY = 20
RADIUS = 70
IN_RANGE = False
ORDERING_RSU_ID = None

last_3_distances = []

def on_connectLamps(client, userdata, flags, rc):
    print(colored("Connected with result code: ", "green"), colored(str(rc), "green"))
    client.subscribe("posts_info")

def on_messageLamps(client, userdata, msg):
    global LAMPS
    message = json.loads(msg.payload)
    LAMPS = message

def on_connectObu(client, userdata, flags, rc):
    print(colored("Connected with result code: ", "green"), colored(str(rc), "green"))
    client.subscribe("vanetza/out/cam")

def on_connectRsu(client, userdata, flags, rc):
    print(colored("Connected with result code: ", "green"), colored(str(rc), "green"))
    client.subscribe("all/lsm")


def on_messageRsu(client, userdata, msg):
    global MY_STATUS, MY_INTENSITY, BIAS, ORDERING_RSU_ID, last_3_distances
    message = json.loads(msg.payload)
    if(message["station_id"] == ID):
        return
    ORDERING_RSU_ID = -1
    dest_stations = message["dest_stations"]
    for key, value in dest_stations.items():
        if key == str(ID):
            # if MY_INTENSITY < value:
            MY_INTENSITY = value
            ORDERING_RSU_ID = message["station_id"]
            print(colored("Intensity received: ", "yellow"), colored(MY_INTENSITY, "yellow"))

def on_messageObu(client, userdata, msg):
    global MY_STATUS, MY_INTENSITY, BIAS, IN_RANGE

    # print(msg.topic+" "+str(msg.payload))

    message = json.loads(msg.payload)
    # check the message parameters "longitude"
    longitude = message["longitude"]

    latitude = message["latitude"]

    velocity = message["speed"]

    distance_between_car_and_post = round(distance((latitude, longitude), (post.x, post.y)).meters,2)
    if(distance_between_car_and_post > RADIUS):
        IN_RANGE = False
        return
    IN_RANGE = True

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
    iluminacao = calc_iluminacao(distance_between_car_and_post,velocity, BIAS, facing)
    MY_INTENSITY = iluminacao

    if iluminacao > 20 and MY_STATUS == "dimmed":
        MY_STATUS = "on"
    
    elif iluminacao <= 20 and MY_STATUS == "on":
        MY_STATUS = "dimmed"

    print(colored("Iluminacao: ", "yellow"), colored(iluminacao, "yellow"))  
    print("\n")

    target_ids = get_post_ids()
    times = get_times_to_arrival(target_ids, latitude, longitude, velocity)
    intensities = get_intensities(times, BIAS)
    out_message = construct_message([2], MY_INTENSITY, intensities)
    publish_lsm(out_message)
    
def publish_lsm(message):
    clientRsu.publish("all/lsm", message) #lsm = light support message
    print(message)
    print("LSM published on all/lsm")

def publish_status(intensity, in_range, ordering_rsu_id):
    if in_range:
        ordering_rsu_id = ID
    message = {
        "station_id": ID,
        "intensity": intensity,
        "in_range": in_range,
        "ordering_rsu_id": ordering_rsu_id
    }
    clientRsu.publish("all/status", json.dumps(message))
    print("Status published on all/status")


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

def construct_message(destination, intensity, intensities):
    f = open('./out_lsm.json')
    m = json.load(f)
    m["dest_stations"] = intensities
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
    if LAMPS == {}:
        return []
    ids = []
    for key, value in LAMPS.items():
        ids.append(key)
    return ids

def get_times_to_arrival(ids, car_latitude, car_longitude, car_speed):
    global LAMPS
    times = {}
    for id in ids:
        distance_between_car_and_post = round(distance((car_latitude, car_longitude), (LAMPS[id]['Latitude'], LAMPS[id]['Longitude'])).meters,2)
        time_to_arrival = round(calc_interval(distance_between_car_and_post, car_speed),2)
        times[id] = time_to_arrival
    return times

def intensity_on_time(tempo, bias):
    # if(not facing_post):
    #    bias = 2
    luminosidade = 1/tempo*100*bias

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 20
    
    return Math.ceil(luminosidade)


def get_intensities(times, bias):
    intensities = {}
    for key, value in times.items():
        temp = intensity_on_time(value, bias)
        if (temp >= 20):
            intensities[key] = temp
    return intensities



clientObu = mqtt.Client()
clientObu.on_connect = on_connectObu
clientObu.on_message = on_messageObu
clientObu.connect(IP, 1883, 60)
threading.Thread(target=clientObu.loop_forever).start()

clientRsu = mqtt.Client()
clientRsu.on_connect = on_connectRsu
clientRsu.on_message = on_messageRsu
clientRsu.connect("192.168.98.1", 1883, 60)
threading.Thread(target=clientRsu.loop_forever).start()

clientLamps = mqtt.Client()
clientLamps.on_connect = on_connectLamps
clientLamps.on_message = on_messageLamps
clientLamps.connect("192.168.98.1", 1883, 60)
threading.Thread(target=clientLamps.loop_forever).start()


def main():
    time.sleep(0.5)
    print("Starting RSU"+str(ID)+"...")
    while True:
        publish_status(MY_INTENSITY, IN_RANGE, ORDERING_RSU_ID)
        time.sleep(0.2)

if __name__ == "__main__":
    main()