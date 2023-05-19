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
# pair_post = post(40.635986, -8.646732)
# post3 = post(40.635995, -8.646634)
# post4 = post(40.635953, -8.646696)

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

MY_STATUS = "off"


#mosquitto_sub -h 192.168.98.20 -t "vanetza/in/cam" -v 
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/in/cam")

def on_message(client, userdata, msg):
    global MY_STATUS

    # print(msg.topic+" "+str(msg.payload))

    message = json.loads(msg.payload)

    # check the message parameters "longitude"
    longitude = message["longitude"]

    latitude = message["latitude"]

    velocity = message["speed"]

    distance_between_car_and_post = distance((latitude, longitude), (post.x, post.y)).meters

    print("Distance between car and post: ", distance_between_car_and_post)

    print("My status: ", MY_STATUS)

    iluminacao = calc_iluminacao(distance_between_car_and_post,velocity)

    if iluminacao > 20 and MY_STATUS == "off":
        MY_STATUS = "on"
        print(colored("Turning on the light ", "magenta"))
        syncronize(syncronize_message)
    
    elif iluminacao < 20 and MY_STATUS == "on":
        print(colored("Turning off the light ", "magenta"))
        MY_STATUS = "off"

    print(colored("Iluminacao: ", "green"), iluminacao,distance_between_car_and_post,velocity)  


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
    client.publish("vanetza/out/lsm", message)
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