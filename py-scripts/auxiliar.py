import time
import json
from termcolor import colored
import paho.mqtt.client as mqtt
from geopy.distance import distance
import threading
import subprocess

# this program should public the posts information to the "192.168.98.1", 1883, 60 and public the content of the file "posts_coordinaates.json"

broker_address = "192.168.98.1"
broker_port = 1883
topic = "posts_info"

obu_lat = 0
obu_lon = 0

client = mqtt.Client()
client.connect(broker_address, broker_port, 60)
client.loop_start()

with open('posts_coordinates.json') as json_file:
    posts = json.load(json_file)

def on_connectObu(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("vanetza/in/cam")

def on_messageObu(client, userdata, msg):
    global obu_lat, obu_lon
    msg = json.loads(msg.payload)
    # print(msg)
    obu_lat = msg['latitude']
    obu_lon = msg['longitude']

    #loop through posts and check if the post is a RSU ("RSU": true)
    #if it is, check if the obu is near the post (distance < 50m)
    #if it is, print "NEAR POST WITH ID: " + post_id
    #if not, print "NOT NEAR POST WITH ID: " + post_id
    print("------------------")
    for key, post in posts.items():
        if post['RSU'] == True:
            post_lat = post['Latitude']
            post_lon = post['Longitude']
            post_coords = (post_lat, post_lon)
            obu_coords = (obu_lat, obu_lon)
            dist = distance(post_coords, obu_coords).meters
            if dist < 70:
                print(colored("NEAR POST WITH ID: " + key, "green"))
                #execute bash command 
                bashCommand = "docker exec rsu"+str(key)+" block 6e:06:e0:03:00:01"
                try:
                    subprocess.run(bashCommand, shell=True, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError as e:
                    pass


            else:
                print(colored("NOT NEAR POST WITH ID: " + key, "red"))
                bashCommand = "docker exec rsu"+str(key)+" unblock 6e:06:e0:03:00:01"
                try:
                    subprocess.run(bashCommand, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError as e:
                    pass

# clientObu = mqtt.Client()
# clientObu.on_connect = on_connectObu
# clientObu.on_message = on_messageObu
# clientObu.connect("192.168.98.10", 1883, 60)
# threading.Thread(target=clientObu.loop_forever).start()

while True:
    with open('posts_coordinates.json') as json_file:
        data = json.load(json_file)
        client.publish(topic, json.dumps(data))
        # print(colored("Published posts information to the MQTT broker", "green"))
    time.sleep(1)
