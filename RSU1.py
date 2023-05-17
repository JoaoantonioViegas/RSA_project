import paho.mqtt.client as mqtt
import time
import json
import random
from geopy.distance import distance
from termcolor import colored

class post:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# post = post(20, 60)
post = post(40.63605, -8.64657)

turn_light_on_message = {
    "my_status": "on",
    "ordering_status": "on",
    "longitude": post.y,
    "latitude": post.x,
    "stationID": 1,
}

syncronize_message = {
    "syncronize": "on",
    "ordering_status": "on",
    "longitude": post.y,
    "latitude": post.x,
    "stationID": 1,
}

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
        print(colored("Turning on the light ", "magenta"))
        MY_STATUS = "on"
        syncronize(json.dumps(turn_light_on_message))

    elif distance_between_car_and_post > 20 and MY_STATUS == "on":
        print(colored("Turning off the light ", "magenta"))
        MY_STATUS = "off"

    elif distance_between_car_and_post >10 and MY_STATUS == "on":
        print(colored("Sending message to the broker","cyan"))
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

def public_message(message):
    client.publish("vanetza/out/lsm", message) #lsm = light support message
    print("Message published")

def syncronize(message):
    client.publish("vanetza/out/sync", message)
    print("Syncronize message published")


def main():
    print("Starting RSU1")
    while True:
        time.sleep(1)






if __name__ == "__main__":
    main()