import paho.mqtt.client as mqtt
import time
import json
import random
from geopy.distance import distance
from termcolor import colored
import math as Math

class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# post = post(20, 60)
post = post(40.636028, -8.646669)
pair_post = post(40.635986, -8.646732)
post3 = post(40.635995, -8.646634)
post4 = post(40.635953, -8.646696)

turn_light_on_message = {
    "my_status": "on",
    "ordering_status": "on",
    "longitude": post.y,
    "latitude": post.x,
    "stationID": 1,
}
turn_light_on_message = json.dumps(turn_light_on_message)


syncronize_message = {
    "syncronize": "on",
    "ordering_status": "on",
    "longitude": post.y,
    "latitude": post.x,
    "stationID": 1,
}
syncronize_message = json.dumps(syncronize_message)

# Falta fazer a gaita para descobrir em que estado esta o poste
MY_STATUS = "off"


#mosquitto_sub -h 192.168.98.20 -t "vanetza/in/cam" -v 
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/in/cam")

def on_message(client, userdata, msg):
    global MY_STATUS

    print(msg.topic+" "+str(msg.payload))

    message = json.loads(msg.payload)

    # check the message parameters "longitude"
    longitude = message["longitude"]

    latitude = message["latitude"]

    distance_between_car_and_post = distance((latitude, longitude), (post.x, post.y)).meters

    print("Distance between car and post: ", distance_between_car_and_post)

    print("My status: ", MY_STATUS)

    if distance_between_car_and_post < 20 and MY_STATUS == "off":
        MY_STATUS = "on"
        print(colored("Turning on the light ", "magenta"))
        syncronize(syncronize_message)

    elif distance_between_car_and_post > 20 and MY_STATUS == "on":
        print(colored("Turning off the light ", "magenta"))
        MY_STATUS = "off"

    elif distance_between_car_and_post >10 and MY_STATUS == "on":
        print(colored("Sending message to the post","cyan"))
        public_message(json.dumps(turn_light_on_message))

    if distance_between_car_and_post < 20 and distance_between_car_and_post > 0 and MY_STATUS == "on":
        # print with another color 
        print(colored("CAR is at: ", "green"),latitude,longitude)
        print(colored("Light is on ", "yellow"))
        
    else:
        print(colored("CAR is at: ", "red"), latitude, longitude)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.98.20", 1883, 60)
client.loop_start()


def main():
    print("Starting RSU1")
    while True:
        time.sleep(1)

def public_message(message):
    client.publish("vanetza/out/lsm", message) #lsm = light support message
    print("Message to next post published")

def syncronize(message):
    client.publish("vanetza/out/sync/1", message)
    print("Syncronize message published")

def calc_iluminacao(distancia, velocidade):
    tempo = calcular_tempo(distancia, velocidade)
    luminosidade = 1/tempo*100*2.3

    if luminosidade > 100:
        luminosidade = 100

    if luminosidade <20:
        luminosidade = 0

    if distancia < 20:
        return 100
    
    return Math.ceil(luminosidade)

def calcular_tempo(distancia, velocidade):
    # Converter a velocidade para metros por segundo
    velocidade_ms = velocidade * (1000/3600)

    # Calcular o tempo em segundos
    tempo = distancia / velocidade_ms

    return tempo


if __name__ == "__main__":
    main()